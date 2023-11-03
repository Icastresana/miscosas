import requests
from bs4 import BeautifulSoup

def scraper():
    url = 'https://hackmd.io/@algamo/DELANTERO-PICHICHI'
    # Definir los encabezados y las cookies
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Referer": "https://hackmd.io",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    }

    cookies = {
    "locale": "es",
    "connect.sid": "s%3AYutx3Z8hIKU7HkY8ygAsTEVHaNawfF0j.18Kq%2F7CUS0cLCsplAY0zlFScsCmYlJUyQhXgMu0YeNg",
    # Otras cookies que puedas necesitar
    }


    try:
        response = requests.get(url)
        response.raise_for_status()  # Verificar si la respuesta tiene éxito (código de estado 200)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        lista = ""
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
            print("scraper : INFO : could not access the website")

    except requests.exceptions.RequestException as e:
        print(f"scraper : ERROR : {e}")

def write_cache(contenido):
    with open("cachedlist.txt", "wb") as cachedlist:
        cachedlist.write(contenido.encode('latin1'))
        cachedlist.close()
        print("scraper : INFO : website data cached")

scraper()
