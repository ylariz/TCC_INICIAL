import io
import contextlib
import traceback

def executar_codigo(codigo, entrada):
    saida = io.StringIO()

    entradas = iter(entrada.splitlines())

    def meu_input(prompt=""):
        print(prompt, end="")
        return next(entradas)

    try:
        with contextlib.redirect_stdout(saida):
            exec(codigo, {"input": meu_input})

        return {
            "sucesso": True,
            "saida": saida.getvalue(),
            "erro": None
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "saida": saida.getvalue(),
            "erro": traceback.format_exc()
        }
