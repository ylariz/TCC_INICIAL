import json
import random
from pathlib import Path

import torch
from torch.utils.data import Dataset

from IA.modelo.tokenizer import tokenizar
from IA.modelo.vocabulario import Vocabulario


class DatasetTutor(Dataset):
    """Lê o intents.json e gera, para cada frase de treino, dois rótulos:
    o tópico (variavel, lista, for...) e o tipo de dúvida (conceito,
    exemplo, erro, comparacao)."""

    def __init__(self, caminho_intents, tamanho_maximo=20, vocabulario=None):
        self.caminho_intents = Path(caminho_intents)
        self.tamanho_maximo = tamanho_maximo
        self.vocabulario = vocabulario or Vocabulario()
        self.prob_desconhecida = 0.0  # o treino liga isso só nas épocas de treino

        with self.caminho_intents.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.intents = dados["intents"]

        # A ordem segue a primeira aparição no arquivo, então é sempre a mesma.
        topicos = list(dict.fromkeys(intent["topico"] for intent in self.intents))
        tipos = list(dict.fromkeys(intent["tipo"] for intent in self.intents))

        self.topico_para_indice = {topico: i for i, topico in enumerate(topicos)}
        self.tipo_para_indice = {tipo: i for i, tipo in enumerate(tipos)}

        self.amostras = []
        for intent in self.intents:
            indice_topico = self.topico_para_indice[intent["topico"]]
            indice_tipo = self.tipo_para_indice[intent["tipo"]]

            for frase in intent["patterns"]:
                tokens = tokenizar(frase)
                self.vocabulario.adicionar_tokens(tokens)
                self.amostras.append((tokens, indice_topico, indice_tipo))

    def __len__(self):
        return len(self.amostras)

    def __getitem__(self, indice):
        tokens, topico, tipo = self.amostras[indice]

        # Durante o treino, algumas palavras viram <UNK> ao acaso (word dropout).
        # Assim a rede aprende a acertar mesmo com palavras que nunca viu,
        # em vez de decorar uma palavra só.
        if self.prob_desconhecida > 0 and len(tokens) > 1:
            tokens = [
                "<UNK>" if random.random() < self.prob_desconhecida else token
                for token in tokens
            ]

        indices = self.vocabulario.preparar_indices(tokens, self.tamanho_maximo)
        entrada = torch.tensor(indices, dtype=torch.long)
        alvo_topico = torch.tensor(topico, dtype=torch.long)
        alvo_tipo = torch.tensor(tipo, dtype=torch.long)
        return entrada, alvo_topico, alvo_tipo

    @property
    def tamanho_vocabulario(self):
        return len(self.vocabulario.palavra_para_indice)

    @property
    def quantidade_topicos(self):
        return len(self.topico_para_indice)

    @property
    def quantidade_tipos(self):
        return len(self.tipo_para_indice)
