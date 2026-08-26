import json
from pathlib import Path

import torch

from inferencia.contexto import Contexto
from inferencia.interpretar import interpretar
from modelo.modelo import RedeTutorPython
from modelo.vocabulario import Vocabulario


RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_MODELO = RAIZ / "pesos" / "modelo.pth"
CAMINHO_INTENTS = RAIZ / "dados" / "intents.json"


class Responder:
    def __init__(self):
        if not CAMINHO_MODELO.exists():
            raise FileNotFoundError(
                "Modelo não encontrado. Execute primeiro: python -m treino.treino"
            )

        checkpoint = torch.load(CAMINHO_MODELO, map_location="cpu", weights_only=False)

        self.vocabulario = Vocabulario()
        self.vocabulario.palavra_para_indice = checkpoint["palavra_para_indice"]
        self.vocabulario.indice_para_palavra = {
            int(indice): palavra
            for indice, palavra in checkpoint["indice_para_palavra"].items()
        }

        self.tag_para_indice = checkpoint["tag_para_indice"]
        self.indice_para_tag = {
            int(indice): tag for tag, indice in self.tag_para_indice.items()
        }
        self.tamanho_maximo = checkpoint["tamanho_maximo"]

        self.modelo = RedeTutorPython(
            checkpoint["tamanho_vocabulario"],
            checkpoint["quantidade_classes"],
        )
        self.modelo.load_state_dict(checkpoint["modelo"])
        self.modelo.eval()

        with CAMINHO_INTENTS.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.respostas = {
            intent["tag"]: intent["responses"] for intent in dados["intents"]
        }
        self.contexto = Contexto()

    def responder(self, pergunta):
        tokens, indices = interpretar(
            pergunta,
            self.vocabulario,
            self.tamanho_maximo,
        )

        entrada = torch.tensor([indices], dtype=torch.long)

        with torch.no_grad():
            saidas = self.modelo(entrada)
            probabilidades = torch.softmax(saidas, dim=1)
            confianca, indice = torch.max(probabilidades, dim=1)

        tag = self.indice_para_tag[indice.item()]
        confianca = confianca.item()

        if confianca < 0.45:
            resposta = (
                "Ainda não tenho confiança suficiente para classificar essa dúvida. "
                "Tente explicar um pouco mais ou envie o código e o erro apresentado."
            )
        else:
            resposta = self.respostas[tag][0]

        self.contexto.adicionar(pergunta, resposta, tag)

        return {
            "resposta": resposta,
            "intencao": tag,
            "confianca": confianca,
            "tokens": tokens,
        }
