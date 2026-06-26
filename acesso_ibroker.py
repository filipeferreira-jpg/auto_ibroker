import os
import time
import requests
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def baixar_jsp(download_dir: str = r"C:\Users\filipe.ferreira\Downloads") -> str:
    """
    Classe que faz download da aplicação Java, acessando diretamente o endereço da bysoft 107.21.0.176:8190,
    o download é feito via Selenium, mas usando requests para pegar o arquivo,
    já que o Selenium tem dificuldades com downloads,
    especialmente quando há proteções de segurança envolvidas.
    O script também tenta desabilitar as proteções de download do Chrome para evitar bloqueios, mas isso nem sempre é 100% eficaz.
    """
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "download.prompt_for_download": False,
        "download.default_directory": download_dir,
    })
    chrome_options.add_argument("--safebrowsing-disable-download-protection")
    chrome_options.add_argument("--disable-features=InsecureDownloadWarnings")

    driver = webdriver.Chrome(options=chrome_options)
    wait   = WebDriverWait(driver, 20)

    try:
        driver.get("http://107.21.0.176:8190/")
        time.sleep(3)
        print("✓ Site acessado com sucesso!")

        icon = wait.until(EC.element_to_be_clickable(
            #Xpath ibroker Import 
            # (By.XPATH, '//*[@id="top"]/div/div[3]/section[1]/ul/li[2]/article/a/i')
            #Xpath ibroker Export
            (By.XPATH, '//*[@id="top"]/div/div[3]/section[2]/ul/li[2]/article/a/i')
        ))
        a    = icon.find_element(By.XPATH, "./ancestor::a[1]")
        href = a.get_attribute("href")

        if not href:
            raise RuntimeError(" O link de download não tem href.")

        file_url = urljoin(driver.current_url, href)
        print(f"✓ URL capturada: {file_url}")

        sess = requests.Session()
        for c in driver.get_cookies():
            sess.cookies.set(c["name"], c["value"])

        resp = sess.get(file_url, stream=True, timeout=60)
        resp.raise_for_status()

        filename = None
        cd = resp.headers.get("Content-Disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[-1].strip().strip('"')
        if not filename:
            path     = urlparse(file_url).path
            filename = os.path.basename(path) or "download.bin"

        dest = os.path.join(download_dir, filename)
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(1024 * 256):
                if chunk:
                    f.write(chunk)

        print(f"✓ Download concluído: {dest}")
        return dest

    finally:
        time.sleep(2)
        driver.quit()