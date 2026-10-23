class Contexto:
    def __init__(self, limite=5):
        self.limite = limite
        self.historico = []

    def adicionar(self, pergunta, resposta, intencao=None, topico=None, origem=None):
        # topico: assunto entendido nessa resposta (None se a Yana não entendeu)
        # origem: de onde veio a resposta ("intents", "extra" ou "fallback")
        self.historico.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "intencao": intencao,
            "topico": topico,
            "origem": origem,
        })

        if len(self.historico) > self.limite:
            self.historico.pop(0)

    def obter_historico(self):
        return list(self.historico)

    def ultimo_entendido(self):
        """Última resposta em que a Yana entendeu o assunto."""
        for item in reversed(self.historico):
            if item.get("topico"):
                return item
        return None

    def limpar(self):
        self.historico.clear()
