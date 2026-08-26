from inferencia.responder import Responder


PERGUNTAS = {
    "1. Faceis (parecidas com o treino)": [
        "o que e uma variavel",
        "como criar uma lista em python",
        "para que serve um dicionario",
        "como definir uma funcao",
        "como usar if e else",
        "como fazer um laco for",
        "qual a diferenca entre for e while",
        "meu programa nao funciona",
    ],
    "2. Reformuladas (testam generalizacao)": [
        "nao sei como guardar um valor numa variavel",
        "quero adicionar um elemento na minha lista",
        "como faco pra pegar um valor dentro do dicionario",
        "minha funcao nao esta retornando nada",
        "como comparo dois numeros em python",
        "meu for esta pulando elementos",
        "meu while nao para de rodar",
        "deu um erro estranho no meu codigo, o que eu faco",
    ],
    "3. Fora do escopo (testam o fallback)": [
        "qual e a capital do brasil",
        "oi, tudo bem?",
        "como faco bolo de chocolate",
        "python e uma linguagem interpretada ou compilada",
    ],
    "4. Casos sujos (testam limpeza de texto)": [
        "COMO CRIAR UMA VARIAVEL???",
        "Como Declarar Uma Variavel Em Python!!",
        "pra que serve lista mesmo",
        "vc sabe pra q serve dicionario",
    ],
    "5. Topicos parecidos (testam confusao entre classes)": [
        "como acesso o primeiro item de uma lista",
        "como acesso um valor pelo nome da chave",
        "for e while fazem a mesma coisa?",
        "posso usar for dentro de um dicionario",
    ],
}


def rodar_bateria():
    bot = Responder()

    for categoria, perguntas in PERGUNTAS.items():
        print("=" * 70)
        print(categoria)
        print("=" * 70)

        for pergunta in perguntas:
            resultado = bot.responder(pergunta)

            print(f"\nPergunta: {pergunta}")
            print(f"  Intencao: {resultado['intencao']}  |  Confianca: {resultado['confianca']:.2%}")
            print(f"  Resposta: {resultado['resposta']}")

        print()


def modo_interativo():
    bot = Responder()

    print("Digite 'sair' para encerrar.\n")

    while True:
        pergunta = input("Voce: ")

        if pergunta.lower() == "sair":
            break

        resultado = bot.responder(pergunta)

        print(f"\nIntencao detectada: {resultado['intencao']} (confianca: {resultado['confianca']:.2%})")
        print(f"Tutor: {resultado['resposta']}\n")


if __name__ == "__main__":
    rodar_bateria()

    print("\nBateria de testes concluida. Quer testar perguntas suas agora? (s/n)")
    resposta = input("> ")

    if resposta.strip().lower() == "s":
        modo_interativo()
