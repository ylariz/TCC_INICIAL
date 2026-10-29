import json
from pathlib import Path

import torch

from IA.inferencia.contexto import Contexto
from IA.inferencia.interpretar import interpretar
from IA.modelo.modelo import RedeTutorPython
from IA.modelo.tokenizer import tokenizar
from IA.modelo.vocabulario import Vocabulario


RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_MODELO = RAIZ / "pesos" / "modelo.pth"
CAMINHO_INTENTS = RAIZ / "dados" / "intents.json"
CAMINHO_CONHECIMENTO = RAIZ / "dados" / "conhecimento" / "python.json"

LIMITE_TOPICO = 0.50
LIMITE_TIPO = 0.45

RESPOSTA_SEM_CONFIANCA = (
    "Ainda não tenho confiança suficiente para classificar essa dúvida. "
    "Tente explicar um pouco mais ou envie o código e o erro apresentado."
)

RESPOSTA_EXEMPLO_SEM_ASSUNTO = (
    "Claro! De qual assunto você quer o exemplo? "
    "Posso mostrar sobre variável, lista, dicionário, função, if/else, for ou while."
)

CONVITE_EXEMPLO = "Quer ver um exemplo prático? É só pedir."

PALAVRAS_PEDIDO_EXEMPLO = {"exemplo", "exemplos", "codigo", "codigos", "pratico", "pratica"}

PALAVRAS_DO_PEDIDO = PALAVRAS_PEDIDO_EXEMPLO | {
    "mostra", "mostrar", "mostre", "outro", "outra", "mais", "ver", "algum", "alguma",
    "tem", "dar", "da", "faz", "faca", "fazer", "quero", "queria", "consegue",
    "simples", "facil",
}

TIPOS_COM_CONVITE = {"conceito", "comparacao"}


class Responder:
    def __init__(self):
        if not CAMINHO_MODELO.exists():
            raise FileNotFoundError(
                "Modelo não encontrado. Execute primeiro: python -m IA.treino.treino"
            )

        checkpoint = torch.load(CAMINHO_MODELO, map_location="cpu", weights_only=False)

        self.vocabulario = Vocabulario()
        self.vocabulario.palavra_para_indice = checkpoint["palavra_para_indice"]
        self.vocabulario.indice_para_palavra = {
            int(indice): palavra
            for indice, palavra in checkpoint["indice_para_palavra"].items()
        }

        self.indice_para_topico = {
            indice: topico for topico, indice in checkpoint["topico_para_indice"].items()
        }
        self.indice_para_tipo = {
            indice: tipo for tipo, indice in checkpoint["tipo_para_indice"].items()
        }
        self.tamanho_maximo = checkpoint["tamanho_maximo"]

        self.modelo = RedeTutorPython(
            checkpoint["tamanho_vocabulario"],
            checkpoint["quantidade_topicos"],
            checkpoint["quantidade_tipos"],
        )
        self.modelo.load_state_dict(checkpoint["modelo"])
        self.modelo.eval()

        with CAMINHO_INTENTS.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.respostas = {
            (intent["topico"], intent["tipo"]): intent["response"]
            for intent in dados["intents"]
        }
        self.palavras_do_dominio = calcular_palavras_do_dominio(dados["intents"])
        self.extras = carregar_extras()
        self.contexto = Contexto()

    def classificar(self, indices):
        entrada = torch.tensor([indices], dtype=torch.long)

        with torch.no_grad():
            saida_topico, saida_tipo = self.modelo(entrada)
            prob_topico = torch.softmax(saida_topico, dim=1)
            prob_tipo = torch.softmax(saida_tipo, dim=1)
            conf_topico, ind_topico = torch.max(prob_topico, dim=1)
            conf_tipo, ind_tipo = torch.max(prob_tipo, dim=1)

        return (
            self.indice_para_topico[ind_topico.item()],
            conf_topico.item(),
            self.indice_para_tipo[ind_tipo.item()],
            conf_tipo.item(),
        )

    def responder(self, pergunta):
        tokens, indices = interpretar(pergunta, self.vocabulario, self.tamanho_maximo)
        topico, conf_topico, tipo, conf_tipo = self.classificar(indices)

        resultado = {
            "intencao": f"{topico}/{tipo}",
            "topico": topico,
            "tipo": tipo,
            "confianca": min(conf_topico, conf_tipo),
            "confianca_topico": conf_topico,
            "confianca_tipo": conf_tipo,
            "tokens": tokens,
        }

        if self.eh_pedido_de_exemplo_sem_assunto(tokens):
            return self.responder_exemplo_do_contexto(pergunta, resultado)

        tem_palavra_do_dominio = any(t in self.palavras_do_dominio for t in tokens)

        entendeu = (
            tem_palavra_do_dominio
            and conf_topico >= LIMITE_TOPICO
            and conf_tipo >= LIMITE_TIPO
            and (topico, tipo) in self.respostas
        )

        if not entendeu:
            resultado["resposta"] = RESPOSTA_SEM_CONFIANCA
            resultado["origem"] = "fallback"
            self.contexto.adicionar(pergunta, RESPOSTA_SEM_CONFIANCA, resultado["intencao"], origem="fallback")
            return resultado

        resposta = self.respostas[(topico, tipo)]
        origem = "intents"

        if tipo in TIPOS_COM_CONVITE and topico in self.extras:
            if any(t in PALAVRAS_PEDIDO_EXEMPLO for t in tokens):
                resposta = f"{resposta}\n\n{montar_resposta_extra(self.extras[topico])}"
                origem = "extra"
            else:
                resposta = f"{resposta}\n\n{CONVITE_EXEMPLO}"

        resultado["resposta"] = resposta
        resultado["origem"] = origem
        self.contexto.adicionar(pergunta, resposta, resultado["intencao"], topico=topico, origem=origem)
        return resultado

    def eh_pedido_de_exemplo_sem_assunto(self, tokens):
        pediu_exemplo = any(t in PALAVRAS_PEDIDO_EXEMPLO for t in tokens)
        citou_assunto = any(
            t in self.palavras_do_dominio and t not in PALAVRAS_DO_PEDIDO for t in tokens
        )
        return pediu_exemplo and not citou_assunto

    def responder_exemplo_do_contexto(self, pergunta, resultado):
        anterior = self.contexto.ultimo_entendido()

        if anterior is None:
            resultado.update({"resposta": RESPOSTA_EXEMPLO_SEM_ASSUNTO, "origem": "fallback"})
            self.contexto.adicionar(pergunta, RESPOSTA_EXEMPLO_SEM_ASSUNTO, origem="fallback")
            return resultado

        topico = anterior["topico"]
        extra = self.extras.get(topico)
        exemplo_do_intents = self.respostas.get((topico, "exemplo"))

        if extra and anterior.get("origem") != "extra":
            resposta, origem = montar_resposta_extra(extra), "extra"
        elif exemplo_do_intents:
            resposta, origem = exemplo_do_intents, "intents"
        else:
            resposta, origem = montar_resposta_extra(extra), "extra"

        resultado.update({
            "resposta": resposta,
            "origem": origem,
            "topico": topico,
            "tipo": "exemplo",
            "intencao": f"{topico}/exemplo",
        })
        self.contexto.adicionar(pergunta, resposta, resultado["intencao"], topico=topico, origem=origem)
        return resultado


def montar_resposta_extra(extra):
    return f"{extra['dia_a_dia']}\n\n```python\n{extra['codigo']}\n```"


def carregar_extras():
    if not CAMINHO_CONHECIMENTO.exists():
        return {}

    with CAMINHO_CONHECIMENTO.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return {
        topico: extra
        for topico, extra in dados.get("extras", {}).items()
        if extra.get("dia_a_dia") and extra.get("codigo")
    }


def calcular_palavras_do_dominio(intents):
    topicos_por_palavra = {}
    nomes_de_topicos = set()

    for intent in intents:
        nomes_de_topicos.update(tokenizar(intent["topico"].replace("_", " ")))
        for frase in intent["patterns"]:
            for palavra in tokenizar(frase):
                topicos_por_palavra.setdefault(palavra, set()).add(intent["topico"])

    quantidade_topicos = len({intent["topico"] for intent in intents})
    limite_generica = quantidade_topicos // 2 + 1

    especificas = {
        palavra
        for palavra, topicos in topicos_por_palavra.items()
        if len(topicos) < limite_generica
    }
    return especificas | nomes_de_topicos
