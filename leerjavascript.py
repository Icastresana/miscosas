from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re

# Configuración de opciones de Chrome para modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Diccionario de URLs principales y sus alternativas
urls = {
    "https://proxy.zeronet.dev/18D6dPcsjLrjg2hhnYqKzNh2W6QtXrDwF": "https://ipfs.io/ipns/elcano.top",
    "https://proxy.zeronet.dev/1JKe3VPvFe35bm1aiHdD4p1xcGCkZKhH3Q": "https://ipfs.io/ipns/k51qzi5uqu5di00365631hrj6m22vsjudpbtw8qpfw6g08gf3lsqdn6e89anq5"
}

# Función para cargar el diccionario desde un archivo externo
def cargar_diccionario(ruta_archivo):
    nombre_canal_map = {}
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        for linea in file:
            if ":" in linea:  # Asegura que la línea tiene el formato correcto
                nombre_final, patron = linea.strip().split(":", 1)  # Divide por el primer ":"
                nombre_canal_map.setdefault(nombre_final, []).append(patron)
    return nombre_canal_map

# Cargar el diccionario desde el archivo externo
nombre_canal_map = cargar_diccionario("canales_map.txt")

def renombrar_canal(nombre_original):
    """Busca si el nombre_original coincide con algún patrón y devuelve (nombre_renombrado, nombre_original)."""
    for nombre_final, patrones in nombre_canal_map.items():
        for patron in patrones:
            if re.match(patron, nombre_original, re.IGNORECASE):  # No distingue mayúsculas/minúsculas
                print(f"🔄 Renombrando: '{nombre_original}' → '{nombre_final}'")  # Debug
                return nombre_final, nombre_original  # Devuelve el renombrado + original

    print(f"✅ Sin cambios: '{nombre_original}'")  # Debug
    return nombre_original, nombre_original  # Si no se renombra, devuelve el mismo nombre 2 veces

# Conjunto de URLs que pertenecen a "Elcano"
urls_elcano = {
    "https://proxy.zeronet.dev/18D6dPcsjLrjg2hhnYqKzNh2W6QtXrDwF",
    "https://ipfs.io/ipns/elcano.top"
}
canales_procesados = set()

# Lista para almacenar nuevos resultados
# Lista para almacenar nuevos resultados con su fuente (principal o alternativa)
nuevos_resultados = []

for principal, alternativa in urls.items():
    url_a_usar = principal  # Intentamos primero con la URL principal
    intentos = 2  # Intentaremos con la principal y luego con la alternativa

    while intentos > 0:
        try:
            print(f"Intentando scrapeo en: {url_a_usar}")

            # Abrir navegador en cada iteración
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url_a_usar)

            # Determinar si la URL pertenece a "Elcano"
            fuente = "elcano" if url_a_usar in urls_elcano else ""


            # Intentar detectar si la página tiene <script> con linksData (estructura alternativa)
            script_elements = driver.find_elements(By.TAG_NAME, "script")
            linksData_found = False

            for script in script_elements:
                script_text = script.get_attribute("innerHTML")
                if "linksData" in script_text:
                    print("Detectada estructura linksData, extrayendo datos...")
                    match = re.search(r'const linksData = ({.*?});', script_text, re.DOTALL)
                    if match:
                        json_data = match.group(1)
                        json_data = json_data.replace("const linksData = ", "").strip(";")  # Limpiar JSON
                        linksData = json.loads(json_data)  # Convertir a diccionario

                        for item in linksData["links"]:
                            nombre_original = item["name"]
                            href = item["url"].replace("acestream://", "")
                            
                            # Aplicar la función de renombrado
                            nombre_renombrado, nombre_original = renombrar_canal(nombre_original)

                            if (nombre_renombrado, href) not in canales_procesados:
                                fuente = "elcano" if url_a_usar == principal else ""
                                nuevos_resultados.append((nombre_renombrado, nombre_original, href, fuente))
                                canales_procesados.add((nombre_renombrado, href))
                            else:
                                print(f"Canal duplicado eliminado: {nombre_original} con ID: {href}")
                        linksData_found = True
                        break  # Ya encontramos la data, no necesitamos revisar más scripts

            if not linksData_found:  # Si no encontró estructura JSON, seguir con el método clásico
                # Esperar a que el iframe esté disponible
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inner-iframe")))
                driver.switch_to.frame("inner-iframe")

                # Esperar a que se carguen los elementos <li>
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))

                # Extraer información de cada <li>
                items = driver.find_elements(By.TAG_NAME, "li")

                for item in items:
                    try:
                        nombre_original = item.find_element(By.CLASS_NAME, 'link-name').text
                        enlace_div = item.find_element(By.CLASS_NAME, 'link-url')
                        enlace = enlace_div.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        href = enlace.replace("acestream://", "")

                        # Aplicar la función de renombrado
                        nombre_renombrado, nombre_original = renombrar_canal(nombre_original)

                        if (nombre_renombrado, href) not in canales_procesados:
                            fuente = "elcano" if url_a_usar in urls_elcano else ""
                            nuevos_resultados.append((nombre_renombrado, nombre_original, href, fuente))
                            canales_procesados.add((nombre_renombrado, href))
                        else:
                            print(f"Canal duplicado eliminado: {nombre_original} con ID: {href}")
                    except Exception as e:
                        print(f"Error extrayendo datos de un elemento: {e}")

            # Cerrar el navegador y salir del bucle si fue exitoso
            driver.quit()
            break

        except Exception as e:
            print(f"Error al acceder a {url_a_usar}: {e}")
            driver.quit()  # Asegurar que el navegador se cierre
            if url_a_usar == principal:
                print(f"Intentando con URL alternativa: {alternativa}")
                url_a_usar = alternativa  # Cambiamos a la alternativa
            else:
                print("Ambas URLs han fallado.")
                break  # Si ya probamos ambas, salimos
        finally:
            intentos -= 1

# Guardar los resultados en un archivo
if nuevos_resultados:
    with open('enlaces_acestream.txt', 'w', encoding='utf-8') as file:
        for nombre_renombrado, nombre_original, href, fuente in nuevos_resultados:
            if href.strip():  # Verifica que el ID no esté vacío
                if fuente == "elcano":
                    file.write(f'{nombre_renombrado} [{nombre_original} ELCANO]\n{href}\n')
                else:
                    # Si en nombre_original no aparece "New Era" ni "New Loop" y no tiene nada escrito
                    if not nombre_original or ("NEW" not in nombre_original and "Tronoss" not in nombre_original):
                        file.write(f'{nombre_renombrado} [{nombre_original} Elcano Antiguas]\n{href}\n')
                    else:
                        file.write(f'{nombre_renombrado} [{nombre_original}]\n{href}\n')
                

    print("✅ Los enlaces han sido guardados en 'enlaces_acestream.txt'.")
else:
    print("❌ No se encontraron enlaces válidos. No se modificó el archivo.")
