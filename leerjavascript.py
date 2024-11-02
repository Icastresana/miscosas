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

# Inicializar `driver` como `None` al principio para evitar errores
driver = None

try:
    # Inicializar el navegador con las opciones configuradas
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Navegar a la URL
    driver.get('https://proxy.zeronet.dev/18D6dPcsjLrjg2hhnYqKzNh2W6QtXrDwF/')

    # Esperar a que el iframe esté disponible
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inner-iframe")))

    # Cambiar al iframe
    driver.switch_to.frame("inner-iframe")

    # Esperar a que se carguen los elementos <li>
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))

    # Extraer información de cada <li>
    items = driver.find_elements(By.TAG_NAME, "li")
    
    # Lista para almacenar los resultados
    resultados = []

    for item in items:
        # Encontrar nombre del canal
        nombre_canal = item.find_element(By.CLASS_NAME, 'link-name').text

        # Extraer el enlace
        enlace_div = item.find_element(By.CLASS_NAME, 'link-url')
        enlace = enlace_div.find_element(By.TAG_NAME, 'a').get_attribute('href')

        
        # Almacenar en la lista
        resultados.append((nombre_canal, href.replace("acestream://", "")))


    # Crear y escribir en el archivo TXT
    with open('enlaces_acestream.txt', 'w', encoding='utf-8') as file:
        for texto, href in resultados:
            file.write(f'{texto}\n{href}\n')

    print("Los enlaces han sido guardados en 'enlaces_acestream.txt'.")

except Exception as e:
    print(f"Error: {e}")
    if driver:
        print(driver.page_source)  # Imprimir el HTML completo de la página para depuración

finally:
    # Cerrar el navegador solo si fue inicializado
    if driver:
        driver.quit()
