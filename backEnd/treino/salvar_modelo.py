from pathlib import Path

import torch


RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_MODELO = RAIZ / "pesos" / "modelo.pth"


def carregar_checkpoint():
    if not CAMINHO_MODELO.exists():
        raise FileNotFoundError("Arquivo de modelo não encontrado.")

    return torch.load(CAMINHO_MODELO, map_location="cpu", weights_only=False)


def salvar_checkpoint(checkpoint):
    CAMINHO_MODELO.parent.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint, CAMINHO_MODELO)
