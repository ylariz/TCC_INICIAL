class Contexto:
    def __init__(self, limite=5):
        self.limite = limite
        self.historico = []

    def adicionar(self, pergunta, resposta, intencao=None):
        self.historico.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "intencao": intencao,
        })

        if len(self.historico) > self.limite:
            self.historico.pop(0)

    def obter_historico(self):
        return list(self.historico)

    def limpar(self):
        self.historico.clear()
