import sys
import requests
import stem.process

# Configura el controlador de Tor
from stem import Signal
from stem.control import Controller

def set_new_tor_identity():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  # Autenticación con el controlador de Tor
        controller.signal(Signal.NEWNYM)  # Envía una señal para obtener una nueva identidad

def scraper():
    lista = ""
    contenido = ""
    print('scraper : INFO : requesting elcano...', flush=True)

    try:
        set_new_tor_identity()  # Obtén una nueva identidad de Tor
        response = requests.get('https://hackmd.io/@algamo/DELANTERO-PICHICHI', proxies={'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("scraper : INFO : Could not access elcano:", e)
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    for enlace in soup.find_all('a'):
        acelink = enlace.get('href')
        canal = enlace.text

        if not str(acelink).startswith("acestream://") or canal == "aquí":
            pass
        else:
            link = str(acelink).replace("acestream://", "")
            lista += str((canal + "\n" + link + "\n"))
            contenido = ((lista.replace(u'\xa0', u' ')).strip())

    if contenido != "":
        print("scraper : OK : channels retrieved")
        write_cache(contenido)
    else:
        print("scraper : INFO : could not access elcano")

def write_cache(contenido):
    with open("toys/cachedList.txt", "wb") as cachedlist:
        cachedlist.write(contenido.encode('latin1'))
        cachedlist.close()
        print("scraper : INFO : elcano cached")

scraper()
