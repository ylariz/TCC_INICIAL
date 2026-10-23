from pathlib import Path

import random

import torch
from torch.utils.data import DataLoader, random_split

from IA.dados.dataset import DatasetTutor
from IA.modelo.modelo import RedeTutorPython


RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_INTENTS = RAIZ / "dados" / "intents.json"
CAMINHO_MODELO = RAIZ / "pesos" / "modelo.pth"

SEMENTE = 42


def treinar(epocas=60, taxa_aprendizado=0.002, tamanho_lote=16, prob_desconhecida=0.15):
    # Semente fixa: o mesmo treino gera sempre o mesmo resultado
    # (importante para comparar versões e citar números no TCC).
    torch.manual_seed(SEMENTE)
    random.seed(SEMENTE)

    dataset = DatasetTutor(CAMINHO_INTENTS, tamanho_maximo=20)

    if len(dataset) < 2:
        raise ValueError("O dataset precisa de pelo menos duas amostras.")

    print(
        f"Frases: {len(dataset)} | tópicos: {dataset.quantidade_topicos} | "
        f"tipos: {dataset.quantidade_tipos} | vocabulário: {dataset.tamanho_vocabulario}"
    )

    modelo = RedeTutorPython(
        dataset.tamanho_vocabulario,
        dataset.quantidade_topicos,
        dataset.quantidade_tipos,
    )

    tamanho_treino = max(1, int(len(dataset) * 0.8))
    tamanho_validacao = len(dataset) - tamanho_treino

    if tamanho_validacao == 0:
        tamanho_treino -= 1
        tamanho_validacao = 1

    treino, validacao = random_split(
        dataset,
        [tamanho_treino, tamanho_validacao],
        generator=torch.Generator().manual_seed(SEMENTE),
    )

    loader_treino = DataLoader(treino, batch_size=tamanho_lote, shuffle=True)
    loader_validacao = DataLoader(validacao, batch_size=tamanho_lote)

    criterio = torch.nn.CrossEntropyLoss()
    otimizador = torch.optim.Adam(modelo.parameters(), lr=taxa_aprendizado)

    melhor_acuracia = 0.0

    for epoca in range(1, epocas + 1):
        modelo.train()
        dataset.prob_desconhecida = prob_desconhecida
        perda_total = 0.0

        for entradas, alvos_topico, alvos_tipo in loader_treino:
            otimizador.zero_grad()
            saida_topico, saida_tipo = modelo(entradas)

            # A perda total é a soma das perdas das duas tarefas
            perda = criterio(saida_topico, alvos_topico) + criterio(saida_tipo, alvos_tipo)
            perda.backward()
            torch.nn.utils.clip_grad_norm_(modelo.parameters(), max_norm=5.0)
            otimizador.step()
            perda_total += perda.item()

        dataset.prob_desconhecida = 0.0
        acc_topico, acc_tipo, acc_ambos = medir(modelo, loader_validacao)

        # Guarda o modelo que acerta tópico E tipo juntos com mais frequência
        if acc_ambos >= melhor_acuracia:
            melhor_acuracia = acc_ambos
            salvar_checkpoint(modelo, dataset)

        if epoca == 1 or epoca % 10 == 0:
            perda_media = perda_total / max(1, len(loader_treino))
            print(
                f"Epoca {epoca:03d} | perda: {perda_media:.4f} | validação -> "
                f"tópico: {acc_topico:.2%}  tipo: {acc_tipo:.2%}  ambos: {acc_ambos:.2%}"
            )

    print(f"Melhor validação (tópico e tipo certos): {melhor_acuracia:.2%}")
    print(f"Modelo salvo em: {CAMINHO_MODELO}")
    return modelo


def medir(modelo, loader):
    modelo.eval()
    acertos_topico = acertos_tipo = acertos_ambos = total = 0

    with torch.no_grad():
        for entradas, alvos_topico, alvos_tipo in loader:
            saida_topico, saida_tipo = modelo(entradas)
            certo_topico = torch.argmax(saida_topico, dim=1) == alvos_topico
            certo_tipo = torch.argmax(saida_tipo, dim=1) == alvos_tipo

            acertos_topico += certo_topico.sum().item()
            acertos_tipo += certo_tipo.sum().item()
            acertos_ambos += (certo_topico & certo_tipo).sum().item()
            total += alvos_topico.size(0)

    if total == 0:
        return 0.0, 0.0, 0.0

    return acertos_topico / total, acertos_tipo / total, acertos_ambos / total


def salvar_checkpoint(modelo, dataset):
    CAMINHO_MODELO.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "modelo": modelo.state_dict(),
        "tamanho_vocabulario": dataset.tamanho_vocabulario,
        "quantidade_topicos": dataset.quantidade_topicos,
        "quantidade_tipos": dataset.quantidade_tipos,
        "tamanho_maximo": dataset.tamanho_maximo,
        "palavra_para_indice": dataset.vocabulario.palavra_para_indice,
        "indice_para_palavra": dataset.vocabulario.indice_para_palavra,
        "topico_para_indice": dataset.topico_para_indice,
        "tipo_para_indice": dataset.tipo_para_indice,
    }
    torch.save(checkpoint, CAMINHO_MODELO)


if __name__ == "__main__":
    treinar()
