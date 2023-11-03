import requests
import re

def scraper():
    url = 'https://hackmd.io/@algamo/DELANTERO-PICHICHI'

    try:
        response = requests.get(url)
        response.raise_for_status()

        lista = ""
        matches = re.findall(r'\*\*(.*?)\*\*[:arrow_forward:]\(acestream://(.*?)\)', response.text)
        
        # Inicializar variables para el canal actual
        current_channel = ""
        current_links = []

        for match in matches:
            canal = match[0].strip()
            acelink = match[1].strip()
            
            # Si el canal actual es igual al canal anterior, agregar el enlace
            if canal == current_channel:
                current_links.append(acelink)
            else:
                # Si el canal cambió, agregar todos los enlaces del canal anterior
                if current_channel:
                    lista += f"{current_channel}: acestream://{', '.join(current_links)}\n"
                # Establecer el nuevo canal y reiniciar la lista de enlaces
                current_channel = canal
                current_links = [acelink]

        # Agregar la última entrada después de salir del bucle
        if current_channel:
            lista += f"{current_channel}: acestream://{', '.join(current_links)}\n"

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
