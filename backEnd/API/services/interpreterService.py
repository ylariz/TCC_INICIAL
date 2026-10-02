import subprocess
import sys
import textwrap
import traceback


def executar_codigo(codigo, entrada):
    wrapper = f"""
        import traceback

        codigo = {codigo!r}
        entrada = {entrada!r}

        entradas = entrada.splitlines()


        def inputs(mensagem=""):
            if not entradas:
                raise RuntimeError("Não há mais entradas disponíveis.")

            return entradas.pop(0)


        try:
            exec(codigo, {{"input": inputs}})

        except Exception:
            print(traceback.format_exc(), end="")
        """

    try:
        processo = subprocess.Popen(
            [sys.executable, "-u", "-c", textwrap.dedent(wrapper)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        try:
            saida, _ = processo.communicate(timeout=0.2)

            return {
                "sucesso": processo.returncode == 0,
                "saida": saida,
                "erro": None if processo.returncode == 0 else saida
            }

        except subprocess.TimeoutExpired:
            processo.kill()

            saida, _ = processo.communicate()

            return {
                "sucesso": False,
                "saida": saida,
                "erro": "Execução interrompida: limite de tempo excedido."
            }

    except Exception:
        return {
            "sucesso": False,
            "saida": "",
            "erro": traceback.format_exc()
        }