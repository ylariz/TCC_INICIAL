import re
import unicodedata

def remove_acentos(texto):
    texto_padrao = unicodedata.normalize("NFD", texto)

    texto_sem_acentos = "".join(
        caractere
        for caractere in texto_padrao
        if unicodedata.category(caractere) != "Mn"
    )
    return texto_sem_acentos

def limpar_texto(texto):
    texto = texto.strip()
    texto = texto.lower()
    texto = remove_acentos(texto)

    texto = re.sub(r"[^\w\s]", " ", texto)

    palavra = texto.split()
    texto = " ".join(palavra)

    return texto
    