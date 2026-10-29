import os

from API.services.interpreterService import executar_codigo


AVISO_EXECUCAO_DESATIVADA = (
    "A execução de código está desativada na versão publicada do YAPY, por segurança. "
    "Para executar programas, use a versão local do projeto."
)


def execucao_permitida():
    no_render = os.environ.get("RENDER", "").strip().lower() not in ("", "0", "false")
    desativada = os.environ.get("EXECUCAO_DESATIVADA", "").strip().lower() not in ("", "0", "false")
    return not (no_render or desativada)


def executar(request):
    if not execucao_permitida():
        return {
            "sucesso": False,
            "saida": "",
            "erro": AVISO_EXECUCAO_DESATIVADA
        }

    result = executar_codigo(request.codigo, request.entrada)
    
    return result
