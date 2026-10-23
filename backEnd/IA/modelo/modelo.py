import torch
import torch.nn as nn

from IA.modelo.embeddings import Embeddings


class RedeTutorPython(nn.Module):
    """LSTM bidirecional com duas saídas (multitarefa):
    - classificador_topico: qual assunto de Python (variavel, lista, for...)
    - classificador_tipo:   o que o aluno quer (conceito, exemplo, erro, comparacao)

    As duas saídas compartilham os embeddings e a LSTM, então o que a rede
    aprende sobre a frase serve para as duas tarefas ao mesmo tempo."""

    def __init__(
        self,
        tamanho_vocabulario,
        quantidade_topicos,
        quantidade_tipos,
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
        self.classificador_topico = nn.Linear(dimensao_oculta * direcoes, quantidade_topicos)
        self.classificador_tipo = nn.Linear(dimensao_oculta * direcoes, quantidade_tipos)

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
        return self.classificador_topico(oculto_final), self.classificador_tipo(oculto_final)
