from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

# === OPCIONES DE NAVEGADOR ===
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecuta sin ventana
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
)

# === CARGAR DICCIONARIO DE RENOMBRADO ===
def cargar_diccionario(ruta_archivo):
    nombre_canal_map = {}
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        for linea in file:
            if ":" in linea:
                nombre_final, patron = linea.strip().split(":", 1)
                nombre_canal_map.setdefault(nombre_final, []).append(patron)
    return nombre_canal_map

# === RENOMBRAR CANAL SEGÚN DICCIONARIO ===
def renombrar_canal(nombre_original, nombre_canal_map):
    for nombre_final, patrones in nombre_canal_map.items():
        for patron in patrones:
            if re.match(patron, nombre_original, re.IGNORECASE):
                print(f"🔁 Renombrando: '{nombre_original}' → '{nombre_final}'")
                return nombre_final, nombre_original
    print(f"✅ Sin cambios: '{nombre_original}'")
    return nombre_original, nombre_original

# === SCRAPEO PRINCIPAL ===
def scrapear_shickat(diccionario_path="canales_map.txt"):
    print("🔍 Scrapeando canales desde shickat.me...")
    resultados = []
    nombre_canal_map = cargar_diccionario(diccionario_path)

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://shickat.me/")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "canal-card")))
        articulos = driver.find_elements(By.CLASS_NAME, "canal-card")

        for articulo in articulos:
            try:
                # Extraer nombre original sin paréntesis
                span_nombre = articulo.find_element(By.CLASS_NAME, "canal-nombre")
                nombre_original = span_nombre.text
                nombre_original = re.sub(r"\s*\(.*?\)", "", nombre_original).strip()

                # Descartar si contiene palabras clave
                if "elcano" in nombre_original.lower() or "new era vi" in nombre_original.lower():
                    print(f"❌ Canal descartado: {nombre_original}")
                    continue

                # Extraer enlace
                enlace_element = articulo.find_element(By.CLASS_NAME, "acestream-link")
                href = enlace_element.get_attribute("href").replace("acestream://", "").strip()

                # Renombrar
                nombre_renombrado, nombre_original = renombrar_canal(nombre_original, nombre_canal_map)

                resultados.append((nombre_renombrado, nombre_original, href, "New Era VI"))

            except Exception as e:
                print(f"⚠️ Error extrayendo canal: {e}")

    except Exception as e:
        print(f"❌ Error accediendo a shickat.me: {e}")
    finally:
        driver.quit()

    return resultados

# === PRUEBA DIRECTA ===
if __name__ == "__main__":
    canales = scrapear_shickat()
    print(f"\n✅ Total canales válidos encontrados: {len(canales)}")
    for nombre_renombrado, nombre_original, href, fuente in canales:
        print(f"- {nombre_renombrado} [{nombre_original} --> NEW ERA VI]\n{href}\n")

    # === GUARDAR RESULTADOS EN UN TXT ===
    with open("enlaces_shickat.txt", "w", encoding="utf-8") as f:
        for nombre_renombrado, nombre_original, href, fuente in canales:
            f.write(f"{nombre_renombrado} [{nombre_original} --> NEW ERA VI]\n{href}\n")


