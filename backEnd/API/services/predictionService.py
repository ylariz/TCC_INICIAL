from IA.inferencia.responder import Responder

_responder = None


def obter_responder():
    global _responder

    if _responder is None:
        _responder = Responder()

    return _responder


def response(question):
    return obter_responder().responder(question)
