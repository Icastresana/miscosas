from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Inicializar el navegador
driver = webdriver.Chrome()

try:
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
        # Encontrar el enlace dentro del <li>
        enlace = item.find_element(By.TAG_NAME, 'a')
        # Extraer el texto y el href
        texto = enlace.text
        href = enlace.get_attribute('href')

        # Eliminar el prefijo 'acestream://' del enlace
        href_sin_prefijo = href.replace("acestream://", "")
        
        # Almacenar en la lista
        resultados.append((texto, href_sin_prefijo))

    # Crear y escribir en el archivo TXT
    with open('enlaces_acestream.txt', 'w', encoding='utf-8') as file:
        for texto, href in resultados:
            file.write(f'{texto}\n{href}\n')

    print("Los enlaces han sido guardados en 'enlaces_acestream.txt'.")

except Exception as e:
    print(f"Error: {e}")
    print(driver.page_source)  # Imprimir el HTML completo de la página para depuración

finally:
    # Cerrar el navegador
    driver.quit()