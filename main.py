import requests
import re

def scraper():
    url = 'https://hackmd.io/@algamo/DELANTERO-PICHICHI'

    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Response content:")
        print(response.text)

        lista = ""
        matches = re.finditer(r'\*\*(.*?)\*\*(?:\s*\[:arrow_forward:\]\(acestream://(.*?)\))*', response.text)
        for match in matches:
            canal = match.group(1).strip()
            acelinks = re.findall(r'acestream://(.*?)(?=\s*\*\*|$)', match.group(2))  # Encuentra todos los enlaces Acestream
            if acelinks:
                lista += f"{canal}:\n"
                lista += "\n".join([f"acestream://{link}" for link in acelinks]) + "\n"


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
