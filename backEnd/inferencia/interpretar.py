from modelo.tokenizer import tokenizar


def interpretar(pergunta, vocabulario, tamanho_maximo):
    tokens = tokenizar(pergunta)
    indices = vocabulario.preparar_indices(tokens, tamanho_maximo)
    return tokens, indices
