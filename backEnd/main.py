from modelo.vocabulario import Vocabulario
from modelo.tokenizer import tokenizar

frase = input("digita ai: ")

tokens = tokenizar(frase)
txt = Vocabulario()
txt.adicionar_tokens(tokens)

indices = txt.transformar_em_indices(tokens)


print("tokens: ",tokens)
print("vocabulario: ",txt.palavra_para_indice)
print("indices: ", indices)