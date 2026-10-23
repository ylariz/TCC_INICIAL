from IA.inferencia.responder import Responder

# O modelo é carregado uma única vez, na primeira pergunta, e reaproveitado.
# Antes ele era recarregado do disco a cada pergunta, o que deixava a
# resposta mais lenta e fazia a Yana "esquecer" o histórico (Contexto),
# que é usado quando a pessoa pede "me dá um exemplo" logo depois.
_responder = None


def obter_responder():
    global _responder

    if _responder is None:
        _responder = Responder()

    return _responder


def response(question):
    return obter_responder().responder(question)
