from API.services.interpreterService import executar_codigo

def executar(request):
    result = executar_codigo(request.codigo, request.entrada)
    
    return result
