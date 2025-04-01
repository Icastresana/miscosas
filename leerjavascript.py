from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
import requests

# Configuración de opciones de Chrome para modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# URL del archivo de texto
url_acestream = "https://raw.githubusercontent.com/Icastresana/miscosas/17b752d45b2cbcbf7c342eec1ec9e92403d95ec6/enlaces_acestream.txt"

# Función para obtener enlaces de Acestream desde la URL
def obtener_enlaces_acestream():
    response = requests.get(url_acestream)
    response.raise_for_status()
    lines = response.text.splitlines()
    acestream_links = []
    iterator = iter(lines)
    for line in iterator:
        name_original = line.strip()
        if name_original:
            try:
                href = next(iterator).strip()
                if href:
                    acestream_links.append((name_original, href))
            except StopIteration:
                break
    return acestream_links

# Lista de URLs principales
urls = [
    "https://proxy.zeronet.dev/18D6dPcsjLrjg2hhnYqKzNh2W6QtXrDwF",
    "https://proxy.zeronet.dev/1JKe3VPvFe35bm1aiHdD4p1xcGCkZKhH3Q"
]

# Función para cargar el diccionario desde un archivo externo
def cargar_diccionario(ruta_archivo):
    nombre_canal_map = {}
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        for linea in file:
            if ":" in linea:
                nombre_final, patron = linea.strip().split(":", 1)
                nombre_canal_map.setdefault(nombre_final, []).append(patron)
    return nombre_canal_map

# Cargar el diccionario desde el archivo externo
nombre_canal_map = cargar_diccionario("canales_map.txt")

def renombrar_canal(nombre_original):
    for nombre_final, patrones in nombre_canal_map.items():
        for patron in patrones:
            if re.match(patron, nombre_original, re.IGNORECASE):
                print(f" Renombrando: '{nombre_original}' → '{nombre_final}'")
                return nombre_final, nombre_original
    print(f"✅ Sin cambios: '{nombre_original}'")
    return nombre_original, nombre_original

canales_procesados = set()
nuevos_resultados = []
error_ocurrido = False

for i, url in enumerate(urls):
    try:
        print(f"Intentando scrapeo en: {url}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        fuente = "elcano" if i == 0 else "otro"
        
        script_elements = driver.find_elements(By.TAG_NAME, "script")
        linksData_found = False
        
        for script in script_elements:
            script_text = script.get_attribute("innerHTML")
            if "linksData" in script_text:
                print("Detectada estructura linksData, extrayendo datos...")
                match = re.search(r'const linksData = ({.*?});', script_text, re.DOTALL)
                if match:
                    json_data = match.group(1).replace("const linksData = ", "").strip(";")
                    linksData = json.loads(json_data)

                    for item in linksData["links"]:
                        nombre_original = item["name"]
                        href = item["url"].replace("acestream://", "")
                        nombre_renombrado, nombre_original = renombrar_canal(nombre_original)

                        if (nombre_renombrado, href) not in canales_procesados:
                            nuevos_resultados.append((nombre_renombrado, nombre_original, href, fuente))
                            canales_procesados.add((nombre_renombrado, href))
                        else:
                            print(f"Canal duplicado eliminado: {nombre_original} con ID: {href}")
                    linksData_found = True
                    break  

        if not linksData_found:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inner-iframe")))
            driver.switch_to.frame("inner-iframe")
            if i == 0:
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
                items = driver.find_elements(By.TAG_NAME, "li")
                for item in items:
                    try:
                        nombre_original = item.find_element(By.CLASS_NAME, 'link-name').text
                        enlace_div = item.find_element(By.CLASS_NAME, 'link-url')
                        enlace = enlace_div.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        href = enlace.replace("acestream://", "")
                        nombre_renombrado, nombre_original = renombrar_canal(nombre_original)
                        if (nombre_renombrado, href) not in canales_procesados:
                            nuevos_resultados.append((nombre_renombrado, nombre_original, href, fuente))
                            canales_procesados.add((nombre_renombrado, href))
                        else:
                            print(f"Canal duplicado eliminado: {nombre_original} con ID: {href}")
                    except Exception as e:
                        print(f"Error extrayendo datos de un elemento: {e}")
            else:
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "channel-item")))
                canales = driver.find_elements(By.CLASS_NAME, "channel-item")
                for canal in canales:
                    try:
                        nombre_canal_element = canal.find_element(By.CLASS_NAME, "item-name")
                        nombre_original = driver.execute_script("""
                            let element = arguments[0];
                            let clone = element.cloneNode(true);
                            clone.querySelectorAll('span').forEach(span => span.remove());
                            return clone.textContent.trim();
                        """, nombre_canal_element)

                        enlace_element = canal.find_element(By.CLASS_NAME, "item-url")
                        href = enlace_element.text.strip() if enlace_element else "Sin enlace"
                        nombre_renombrado, nombre_original = renombrar_canal(nombre_original)

                        if (nombre_renombrado, href) not in canales_procesados:
                            nuevos_resultados.append((nombre_renombrado, nombre_original, href, fuente))
                            canales_procesados.add((nombre_renombrado, href))
                        else:
                            print(f"Canal duplicado eliminado: {nombre_original} con ID: {href}")
                    except Exception as e:
                        print(f"Error extrayendo datos de un elemento: {e}")
        driver.quit()
         # 📌 Después de la primera URL, obtenemos los enlaces del archivo remoto
        if i == 0:
            print("📥 Obteniendo enlaces del archivo remoto...")
            acestream_links = obtener_enlaces_acestream()
            for nombre_original, href in acestream_links:
                 # 🔹 Si el nombre contiene "Especial", lo eliminamos
                if "Especial" in nombre_original:
                    print(f"❌ Canal eliminado: {nombre_original} (contiene 'Especial')")
                    continue  # Saltamos a la siguiente iteración del bucle
                nombre_renombrado, nombre_original = renombrar_canal(nombre_original)
                # 🔹 Agregamos "Elcano Antiguas" al nombre original
                nombre_original = f"{nombre_original} Elcano Antiguas"
                if (nombre_renombrado, href) not in canales_procesados:
                    nuevos_resultados.append((nombre_renombrado, nombre_original, href, "archivo"))
                    canales_procesados.add((nombre_renombrado, href))
                else:
                    print(f"Canal duplicado eliminado: {nombre_original} con ID: {href}")
    except Exception as e:
        print(f"Error al acceder a {url}: {e}")
        driver.quit()
        error_ocurrido = True


# Solo guardar el archivo si no ha ocurrido ningún error
if nuevos_resultados and not error_ocurrido:
    with open('enlaces_acestream.txt', 'w', encoding='utf-8') as file:
        for nombre_renombrado, nombre_original, href, fuente in nuevos_resultados:
            if href.strip():
                if fuente == "elcano":
                    file.write(f'{nombre_renombrado} [{nombre_original} ELCANO]\n{href}\n')
                #elif fuente == "otro":
                    #file.write(f'{nombre_renombrado} [{nombre_original} OTRO]\n{href}\n')
                else:
                    if not nombre_original or ("NEW" not in nombre_original and "Tronoss" not in nombre_original):
                        nombre_modificado = nombre_original.replace("ELCANO", "Elcano Antiguas")
                        file.write(f'{nombre_renombrado} [{nombre_modificado}]\n{href}\n')
                    else:
                        file.write(f'{nombre_renombrado} [{nombre_original}]\n{href}\n')

    print("✅ Los enlaces han sido guardados en 'enlaces_acestream.txt'.")
else:
    print("❌ No se encontraron enlaces válidos o ocurrió un error. No se modificó el archivo.")
