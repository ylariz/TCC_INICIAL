class Vocabulario:
    def __init__(self):
        self.palavra_para_indice = {"<PAD>": 0, "<UNK>": 1}
        self.indice_para_palavra = {0: "<PAD>", 1: "<UNK>"}

    def adicionar_palavra(self, palavra):
        if palavra in self.palavra_para_indice:
            return
        indice = len(self.palavra_para_indice)
        self.palavra_para_indice[palavra] = indice
        self.indice_para_palavra[indice] = palavra

    def adicionar_tokens(self, tokens):
        for token in tokens:
            self.adicionar_palavra(token)

    def obter_indice(self, palavra):
        return self.palavra_para_indice.get(palavra, self.palavra_para_indice["<UNK>"])

    def obter_palavra(self, indice):
        return self.indice_para_palavra.get(indice, "<UNK>")

    def transformar_em_indices(self, tokens):
        return [self.obter_indice(token) for token in tokens]

    def truncar_indices(self, indices, tamanho_maximo):
        return indices[:tamanho_maximo]

    def adicionar_padding(self, indices, tamanho_maximo):
        return indices + [self.palavra_para_indice["<PAD>"]] * (tamanho_maximo - len(indices))

    def preparar_indices(self, tokens, tamanho_maximo):
        indices = self.transformar_em_indices(tokens)
        indices = self.truncar_indices(indices, tamanho_maximo)
        return self.adicionar_padding(indices, tamanho_maximo)
