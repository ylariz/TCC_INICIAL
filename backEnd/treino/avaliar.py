from pathlib import Path

import torch
from torch.utils.data import DataLoader

from dados.dataset import DatasetTutor
from modelo.modelo import RedeTutorPython


RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_INTENTS = RAIZ / "dados" / "intents.json"
CAMINHO_MODELO = RAIZ / "pesos" / "modelo.pth"


def avaliar():
    if not CAMINHO_MODELO.exists():
        raise FileNotFoundError("Treine o modelo antes de avaliá-lo.")

    checkpoint = torch.load(CAMINHO_MODELO, map_location="cpu", weights_only=False)
    dataset = DatasetTutor(
        CAMINHO_INTENTS,
        tamanho_maximo=checkpoint["tamanho_maximo"],
    )

    modelo = RedeTutorPython(
        checkpoint["tamanho_vocabulario"],
        checkpoint["quantidade_classes"],
    )
    modelo.load_state_dict(checkpoint["modelo"])
    modelo.eval()

    loader = DataLoader(dataset, batch_size=16)
    acertos = 0
    total = 0

    with torch.no_grad():
        for entradas, alvos in loader:
            saidas = modelo(entradas)
            previsoes = torch.argmax(saidas, dim=1)
            acertos += (previsoes == alvos).sum().item()
            total += alvos.size(0)

    acuracia = acertos / total if total else 0.0
    print(f"Acuracia no dataset: {acuracia:.2%}")
    return acuracia


if __name__ == "__main__":
    avaliar()
