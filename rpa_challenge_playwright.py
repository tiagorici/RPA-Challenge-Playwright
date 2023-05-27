
# Realiza os imports das Libs utilizadas
import os
import pandas as pd  # pip install pandas
from playwright.sync_api import sync_playwright  # pip install playwright | playwright install

# Inicializa variáveis
browser_channel = 'msedge'
browser_path = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
download_path = os.path.dirname(os.path.abspath(__file__))

# Inicializa o navegador
pw = sync_playwright().start()
browser = pw.chromium.launch(channel=browser_channel,
                             executable_path=browser_path,
                             downloads_path=download_path,
                             headless=False)
page = browser.new_page()

# Navega para URL e aguarda o elemento de validação
page.goto('https://rpachallenge.com')
download_button = page.wait_for_selector('//a[contains(text(), "Download Excel")]')

# Aguarda o download que será realizado após o click no elemento
with page.expect_download() as download_info:
    download_button.click()

# Valida se o arquivo já existe no diretório. Se existir, deleta
file_path = download_path + f'\\{download_info.value.suggested_filename}'
if os.path.exists(file_path):
    os.remove(file_path)

# Renomeia o arquivo baixado para o nome correto
os.rename(download_info.value.path(), file_path)

# Realiza a leitura do arquivo excel
excel = pd.read_excel(file_path)

# Clica no botão "Start" e aguarda a mudança do elemento para iniciar
page.click('//button[text() = "Start"]')
page.wait_for_selector('//button[text() = "Round 1"]')

# Percorre a lista de campos
for row in excel.iterrows():
    for column in excel.columns:
        # Preenche os dados
        page.evaluate('([element, new_value]) => element.value = new_value',
                      [page.query_selector(f'//label[text() = "{column.strip()}"]/following-sibling::input'), row[1][column]])

    # Click no botão "SUBMIT" e aguarda a mudança de página
    page.click('//input[@value = "Submit"]')

# Aguarda o elemento estar visível na tela
success_message = page.wait_for_selector('//div[contains(text(), "Your success rate is")]')

# Captura e imprime o texto
print(success_message.get_property('innerText'))

# Finaliza o navegador
browser.close()
pw.stop()
