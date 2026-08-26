import torch
import torch.nn as nn

from modelo.embeddings import Embeddings


class RedeTutorPython(nn.Module):
    def __init__(self, tamanho_vocabulario, quantidade_classes, dimensao_embedding=64, dimensao_oculta=64):
        super().__init__()

        self.embeddings = Embeddings(tamanho_vocabulario, dimensao_embedding)
        self.rede = nn.Sequential(
            nn.Linear(dimensao_embedding, dimensao_oculta),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(dimensao_oculta, quantidade_classes),
        )

    def forward(self, indices):
        vetores = self.embeddings(indices)
        mascara = (indices != 0).unsqueeze(-1)
        vetores = vetores * mascara
        soma = vetores.sum(dim=1)
        quantidade = mascara.sum(dim=1).clamp(min=1)
        media = soma / quantidade
        return self.rede(media)
