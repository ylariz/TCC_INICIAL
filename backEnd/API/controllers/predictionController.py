from API.services.predictionService import response

def pergunta(request):
    resposta = {"resposta": response(request.text)}
    return resposta