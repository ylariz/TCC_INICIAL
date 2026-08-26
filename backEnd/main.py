from modelo.vocabulario import Vocabulario
from modelo.tokenizer import tokenizar


txt = Vocabulario()

frase_treinamento = "como criar uma lista"

tokens_treinamento = tokenizar(frase_treinamento)

txt.adicionar_tokens(tokens_treinamento)


frase = input("Digita ai: ")

tokens = tokenizar(frase)

indices = txt.preparar_indices(tokens, 6)


print("Tokens:", tokens)
print("Vocabulário:", txt.palavra_para_indice)
print("Índices:", indices)