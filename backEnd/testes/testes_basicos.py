from modelo.tokenizer import tokenizar
from modelo.vocabulario import Vocabulario


def testar_tokenizador():
    tokens = tokenizar("Como criar uma variável?")
    assert tokens == ["como", "criar", "uma", "variavel"]


def testar_vocabulario():
    vocabulario = Vocabulario()
    vocabulario.adicionar_tokens(["como", "criar", "lista"])

    assert vocabulario.obter_indice("como") == 2
    assert vocabulario.obter_indice("desconhecida") == 1


def testar_padding():
    vocabulario = Vocabulario()
    resultado = vocabulario.preparar_indices(["como", "criar"], 5)
    assert len(resultado) == 5
    assert resultado[-1] == 0


if __name__ == "__main__":
    testar_tokenizador()
    testar_vocabulario()
    testar_padding()
    print("Testes básicos aprovados.")
