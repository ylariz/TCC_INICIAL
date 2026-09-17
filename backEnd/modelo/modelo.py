import torch
import torch.nn as nn

from modelo.embeddings import Embeddings


class RedeTutorPython(nn.Module):
    def __init__(
        self,
        tamanho_vocabulario,
        quantidade_classes,
        dimensao_embedding=64,
        dimensao_oculta=64,
        num_camadas=1,
        bidirecional=True,
        dropout=0.3,
    ):
        super().__init__()

        self.embeddings = Embeddings(tamanho_vocabulario, dimensao_embedding)
        self.lstm = nn.LSTM(
            input_size=dimensao_embedding,
            hidden_size=dimensao_oculta,
            num_layers=num_camadas,
            batch_first=True,
            bidirectional=bidirecional,
            dropout=dropout if num_camadas > 1 else 0.0,
        )

        direcoes = 2 if bidirecional else 1
        self.dropout = nn.Dropout(dropout)
        self.classificador = nn.Linear(dimensao_oculta * direcoes, quantidade_classes)

    def forward(self, indices):
        comprimentos = (indices != 0).sum(dim=1).clamp(min=1).cpu()

        vetores = self.embeddings(indices)
        pacote = nn.utils.rnn.pack_padded_sequence(
            vetores, comprimentos, batch_first=True, enforce_sorted=False
        )

        _, (oculto, _) = self.lstm(pacote)

        if self.lstm.bidirectional:
            oculto_final = torch.cat((oculto[-2], oculto[-1]), dim=1)
        else:
            oculto_final = oculto[-1]

        oculto_final = self.dropout(oculto_final)
        return self.classificador(oculto_final)