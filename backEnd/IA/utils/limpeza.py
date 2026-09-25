import re
import unicodedata


def remover_acentos(texto):
    texto_normalizado = unicodedata.normalize("NFD", texto)
    texto_sem_acentos = "".join(
        caractere
        for caractere in texto_normalizado
        if unicodedata.category(caractere) != "Mn"
    )
    return texto_sem_acentos


def limpar_texto(texto):
    texto = texto.strip().lower()
    texto = remover_acentos(texto)
    texto = re.sub(r"[^\w\s]", " ", texto)
    palavras = texto.split()
    return " ".join(palavras)
