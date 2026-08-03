class Vocabulario:
    def __init__(self):
        self.palavra_para_indice = {}

    def adicionar_palavra(self, palavra):
        if palavra in self.palavra_para_indice:
            return
        
        indice = len(self.palavra_para_indice)
        self.palavra_para_indice[palavra] = indice

    def adicionar_tokens(self, tokens):
        for token in tokens:
            self.adicionar_palavra(token)

    def obter_indice(self,palavra):
        return self.palavra_para_indice[palavra]

    def transformar_em_indices(self, tokens):
        indices = []

        for token in tokens:
            indice = self.obter_indice(token)
            indices.append(indice)

        return indices