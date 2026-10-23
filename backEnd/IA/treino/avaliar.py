from pathlib import Path

import torch
from torch.utils.data import DataLoader

from IA.dados.dataset import DatasetTutor
from IA.modelo.modelo import RedeTutorPython
from IA.treino.treino import medir


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
        checkpoint["quantidade_topicos"],
        checkpoint["quantidade_tipos"],
    )
    modelo.load_state_dict(checkpoint["modelo"])
    modelo.eval()

    loader = DataLoader(dataset, batch_size=32)
    acc_topico, acc_tipo, acc_ambos = medir(modelo, loader)

    print(f"Acurácia no dataset -> tópico: {acc_topico:.2%}  tipo: {acc_tipo:.2%}  ambos: {acc_ambos:.2%}")
    return acc_ambos


if __name__ == "__main__":
    avaliar()
