import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader, random_split

from dados.dataset import DatasetTutor
from modelo.modelo import RedeTutorPython


RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_INTENTS = RAIZ / "dados" / "intents.json"
CAMINHO_MODELO = RAIZ / "pesos" / "modelo.pth"


def treinar(epocas=150, taxa_aprendizado=0.001, tamanho_lote=8):
    dataset = DatasetTutor(CAMINHO_INTENTS, tamanho_maximo=12)

    if len(dataset) < 2:
        raise ValueError("O dataset precisa de pelo menos duas amostras.")

    modelo = RedeTutorPython(
        dataset.tamanho_vocabulario,
        dataset.quantidade_classes,
    )

    tamanho_treino = max(1, int(len(dataset) * 0.8))
    tamanho_validacao = len(dataset) - tamanho_treino

    if tamanho_validacao == 0:
        tamanho_treino -= 1
        tamanho_validacao = 1

    treino, validacao = random_split(
        dataset,
        [tamanho_treino, tamanho_validacao],
        generator=torch.Generator().manual_seed(42),
    )

    loader_treino = DataLoader(treino, batch_size=tamanho_lote, shuffle=True)
    loader_validacao = DataLoader(validacao, batch_size=tamanho_lote)

    criterio = torch.nn.CrossEntropyLoss()
    otimizador = torch.optim.Adam(modelo.parameters(), lr=taxa_aprendizado)

    melhor_acuracia = 0.0

    for epoca in range(1, epocas + 1):
        modelo.train()
        perda_total = 0.0

        for entradas, alvos in loader_treino:
            otimizador.zero_grad()
            saidas = modelo(entradas)
            perda = criterio(saidas, alvos)
            perda.backward()
            torch.nn.utils.clip_grad_norm_(modelo.parameters(), max_norm=5.0)
            otimizador.step()
            perda_total += perda.item()

        modelo.eval()
        acertos = 0
        total = 0

        with torch.no_grad():
            for entradas, alvos in loader_validacao:
                saidas = modelo(entradas)
                previsoes = torch.argmax(saidas, dim=1)
                acertos += (previsoes == alvos).sum().item()
                total += alvos.size(0)

        acuracia = acertos / total if total else 0.0

        if acuracia >= melhor_acuracia:
            melhor_acuracia = acuracia
            salvar_checkpoint(modelo, dataset)

        if epoca == 1 or epoca % 10 == 0:
            perda_media = perda_total / max(1, len(loader_treino))
            print(
                f"Epoca {epoca:03d} | perda: {perda_media:.4f} | "
                f"validacao: {acuracia:.2%}"
            )

    print(f"Modelo salvo em: {CAMINHO_MODELO}")
    return modelo


def salvar_checkpoint(modelo, dataset):
    checkpoint = {
        "modelo": modelo.state_dict(),
        "tamanho_vocabulario": dataset.tamanho_vocabulario,
        "quantidade_classes": dataset.quantidade_classes,
        "tamanho_maximo": dataset.tamanho_maximo,
        "palavra_para_indice": dataset.vocabulario.palavra_para_indice,
        "indice_para_palavra": dataset.vocabulario.indice_para_palavra,
        "tag_para_indice": dataset.tag_para_indice,
    }
    torch.save(checkpoint, CAMINHO_MODELO)


if __name__ == "__main__":
    treinar()
