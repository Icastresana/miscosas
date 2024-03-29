import requests
import re

def scraper():
    url = 'https://hackmd.io/@penaltis/YELLOW-CARD'

    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Response content:")
        print(response.text)

        lista = ""
        matches = re.findall(r'\*\*(.*?)\*\*([^*]+)', response.text)
        for match in matches:
            canal = match[0].strip()
            acelinks = re.findall(r'\(acestream://(.*?)\)', match[1])
            if not acelinks:
                acelinks = [""]  # Agrega una cadena vacía si no se encontraron enlaces
            if "WINDOWS ACESTREAM" not in canal and "ANDROID ACESTREAM.APK" not in canal and "AQUÍ" not in canal and "EUR / RU / NA / SA - TV" not in canal and "ESP - TV" not in canal:
                if "720p" in canal:
                    canal_anterior = re.sub(r'1080[p]?', '', canal_anterior)  # Elimina "1080p" o "1080" del nombre anterior
                    canal_anterior = re.sub(r' MultiAudio', '',canal_anterior) # Elimina "multiaudio" del nombre anterior
                    canal = canal_anterior + canal  # Agrega el nombre del canal anterior
                canal_anterior = canal  # Actualiza el nombre del canal anterior
                for acelink in acelinks:
                    lista += f"{canal}:\nacestream://{acelink}\n"




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
