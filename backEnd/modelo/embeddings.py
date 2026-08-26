import torch.nn as nn


class Embeddings(nn.Module):
    def __init__(self, tamanho_vocabulario, dimensao_embedding, indice_padding=0):
        super().__init__()
        self.embedding = nn.Embedding(
            tamanho_vocabulario,
            dimensao_embedding,
            padding_idx=indice_padding,
        )

    def forward(self, indices):
        return self.embedding(indices)
