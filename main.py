import requests
import re

def scraper():
    url = 'https://telegra.ph/EL-PLAN-DEPORTES-03-19'

    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Response content:")
        print(response.text)

        # Patrón de expresión regular para eliminar caracteres no deseados del nombre del canal
        patron = re.compile(r'^\W*')
        lista = ""
        matches = re.findall(r'<p>([^<]+)<\/p>\s*<p>(?:acestream:\/\/)?([0-9a-fA-F]+)<\/p>', response.text)
        for match in matches:
            canal = patron.sub('', match[0].strip())  # Limpiar el nombre del canal
            acelinks = match[1]
            lista += f"{canal}:\nacestream://{acelinks}\n"


        contenido = ((lista.replace(u'\xa0', u' ')).strip())

        if contenido != "":
            print("scraper : OK : channels retrieved")
            write_cache(contenido)
        else:
            print("scraper : INFO : could not access the website")

    except requests.exceptions.RequestException as e:
        print(f"scraper : ERROR : {e}")


def write_cache(contenido):
    with open("cachedlist.txt", "w", encoding='utf-8') as cachedlist:
        cachedlist.write(contenido)
        print("scraper : INFO : website data cached")

scraper()
