from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración de opciones de Chrome para modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Lista de URLs a scrapear
urls = [
    "https://proxy.zeronet.dev/18D6dPcsjLrjg2hhnYqKzNh2W6QtXrDwF",
    "https://proxy.zeronet.dev/1JKe3VPvFe35bm1aiHdD4p1xcGCkZKhH3Q"
]

# Lista para almacenar todos los resultados
resultados = []

for url in urls:
    try:
        print(f"Scrapeando: {url}")

        # Abrir un nuevo navegador en cada iteración
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)

        # Esperar a que el iframe esté disponible
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inner-iframe")))

        # Cambiar al iframe
        driver.switch_to.frame("inner-iframe")

        # Esperar a que se carguen los elementos <li>
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))

        # Extraer información de cada <li>
        items = driver.find_elements(By.TAG_NAME, "li")

        for item in items:
            try:
                nombre_canal = item.find_element(By.CLASS_NAME, 'link-name').text
                enlace_div = item.find_element(By.CLASS_NAME, 'link-url')
                enlace = enlace_div.find_element(By.TAG_NAME, 'a').get_attribute('href')
                href = enlace.replace("acestream://", "")
                resultados.append((nombre_canal, href))
            except Exception as e:
                print(f"Error extrayendo datos de un elemento: {e}")

        # Cerrar el navegador después de procesar la URL
        driver.quit()

    except Exception as e:
        print(f"Error en {url}: {e}")

# Guardar todos los resultados en un archivo
with open('enlaces_acestream.txt', 'w', encoding='utf-8') as file:
    for nombre, href in resultados:
        file.write(f'{nombre}\n{href}\n')

print("Los enlaces han sido guardados en 'enlaces_acestream.txt'.")
