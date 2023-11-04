import requests
import re

def scraper():
    url = 'https://hackmd.io/@algamo/DELANTERO-PICHICHI'

    try:
        response = requests.get(url)
        response.raise_for_status()

        lista = ""
        matches = re.finditer(r'\*\*(.*?)\*\*\(acestream://(.*?)\)$', response.text)

        canales = {}
        canal_actual = None

        for match in matches:
            canal, enlace = match.groups()

            if canal_actual != canal:
                if canal_actual:
                    if canales[canal_actual]:
                        lista += f"{canal_actual}\n" + "\n".join(canales[canal_actual]) + "\n"
                    else:
                        lista += f"{canal_actual}\n"
                canal_actual = canal
                canales[canal] = []

            if enlace:
                canales[canal].append(f"acestream://{enlace}")

        if canal_actual:
            if canales[canal_actual]:
                lista += f"{canal_actual}\n" + "\n".join(canales[canal_actual]) + "\n"
            else:
                lista += f"{canal_actual}\n"

        contenido = ((lista.replace(u'\xa0', u' ')).strip())

        if contenido:
            print("scraper: OK: channels retrieved")
            write_cache(contenido)
        else:
            print("scraper: INFO: could not access the website")

    except requests.exceptions.RequestException as e:
        print(f"scraper: ERROR: {e}")

def write_cache(contenido):
    with open("cachedlist.txt", "w", encoding='utf-8') as cachedlist:
        cachedlist.write(contenido)
        print("scraper: INFO: website data cached")

scraper()
