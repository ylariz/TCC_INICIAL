import json
from pathlib import Path

import torch
from torch.utils.data import Dataset

from modelo.tokenizer import tokenizar
from modelo.vocabulario import Vocabulario


class DatasetTutor(Dataset):
    def __init__(self, caminho_intents, tamanho_maximo=12, vocabulario=None):
        self.caminho_intents = Path(caminho_intents)
        self.tamanho_maximo = tamanho_maximo
        self.vocabulario = vocabulario or Vocabulario()

        with self.caminho_intents.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.intents = dados["intents"]
        self.tag_para_indice = {
            intent["tag"]: indice for indice, intent in enumerate(self.intents)
        }
        self.indice_para_tag = {
            indice: tag for tag, indice in self.tag_para_indice.items()
        }

        self.amostras = []
        for intent in self.intents:
            for frase in intent["patterns"]:
                tokens = tokenizar(frase)
                self.vocabulario.adicionar_tokens(tokens)
                self.amostras.append((tokens, self.tag_para_indice[intent["tag"]]))

    def __len__(self):
        return len(self.amostras)

    def __getitem__(self, indice):
        tokens, classe = self.amostras[indice]
        indices = self.vocabulario.preparar_indices(tokens, self.tamanho_maximo)
        entrada = torch.tensor(indices, dtype=torch.long)
        alvo = torch.tensor(classe, dtype=torch.long)
        return entrada, alvo

    @property
    def tamanho_vocabulario(self):
        return len(self.vocabulario.palavra_para_indice)

    @property
    def quantidade_classes(self):
        return len(self.tag_para_indice)
