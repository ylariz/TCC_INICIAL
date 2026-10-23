from API.services.predictionService import response

def pergunta(request):
    res = response(request.text)
    resposta = {
        "resposta": res["resposta"],
        "intencao": res["intencao"],
        "confianca": res["confianca"],
    }
    return resposta
