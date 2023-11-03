import requests
import re

def scraper():
    url = 'https://hackmd.io/@algamo/DELANTERO-PICHICHI'

    try:
        response = requests.get(url)
        response.raise_for_status()
        

        lista = ""
        matches = re.findall(r'\*\*(.*?)\*\*\(acestream://(.*?)\)', response.text)
        for match in matches:
            canal = match[0].strip()
            acelink = match[1].strip()
            lista += f"{canal}:\n acestream://{acelink}\n"

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
        cachedlist.close()
        print("scraper : INFO : website data cached")

scraper()
