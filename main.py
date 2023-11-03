import requests
import re
import re



def scraper():
    url = 'https://hackmd.io/@algamo/DELANTERO-PICHICHI'

    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Response content:")
        print(response.text)

       # ...
    matches = re.findall(r'\*\*(.*?)\*\*\[:arrow_forward:\]\(acestream://(.*?)(?:\s*[/\\n\\r\\s]+|$)', response.text)
    canal_actual = ""
    lista = ""

    for match in matches:
    canal = match[0].strip()
    acelink = match[1].strip()
    
        if canal == canal_actual:
        # El canal actual tiene múltiples enlaces, así que los agregamos
        lista += f"acestream://{acelink}\n"
        else:
        # Cambio de canal, guardamos el canal anterior y sus enlaces
        if canal_actual:
            lista += f"{canal_actual}:\n{lista}\n"
        canal_actual = canal
        lista = f"acestream://{acelink}\n"

# Asegúrate de agregar el último canal y sus enlaces
if canal_actual:
    lista += f"{canal_actual}:\n{lista}\n"

# ...

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
