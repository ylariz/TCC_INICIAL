from IA.inferencia.responder import Responder

def response(question):
    respostas = Responder()
    res = respostas.responder(question)
    return res["resposta"]