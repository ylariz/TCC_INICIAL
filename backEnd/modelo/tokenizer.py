from utils.limpeza import limpar_texto


def tokenizar(texto):
    texto_limpo = limpar_texto(texto)

    if texto_limpo == "":
        return []

    return texto_limpo.split()
