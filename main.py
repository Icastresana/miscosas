import sys
from bs4 import BeautifulSoup
from torpy.http.requests import TorRequests
import requests

def scraper():
    lista = ""
    print('scraper : INFO : requesting elplan...', flush=True)

    try:
        with TorRequests() as tor_requests:
            with tor_requests.get_session() as sess:
                grab = sess.get('https://hackmd.io/@algamo/DELANTERO-PICHICHI')
                print(grab)
    except Exception as e:
        print(f"scraper : INFO : torpy linea 22 could not access elcano ({e})")
        return  # Return instead of exiting the program

    soup = BeautifulSoup(grab.text, 'html.parser')
    for enlace in soup.find_all('a'):
        acelink = enlace.get('href')
        canal = enlace.text

        if not str(acelink).startswith("acestream://") or canal == "aquÃ­":
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
    with open("cachedlist.txt", "wb") as cachedlist:
        cachedlist.write(contenido.encode('latin1'))
        print("scraper : INFO : elcano cached")

scraper()
