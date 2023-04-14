from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
driver.get('https://www.etf.com/etfanalytics/etf-finder')

time.sleep(5)

botao_100 = driver.find_element("xpath", '/html/body/div[5]/section/div/div[3]/section/div/div/div/div/div[2]/section[2]/div[2]/section[2]/div[1]/div/div[4]/button/label/span')
botao_100.click()

numero_paginas = driver.find_element("xpath", '//*[@id="totalPages"]')
numero_paginas = numero_paginas.text.replace("of ", "")
numero_paginas = int(numero_paginas)

elemento = driver.find_element("xpath", '//*[@id="finderTable"]')
html_tabela = elemento.get_attribute('outerHTML')
tabela = pd.read_html(str(html_tabela))[0]

lista_tabela_por_pagina = []
elemento = driver.find_element("xpath", '//*[@id="finderTable"]')
for pagina in range(1, numero_paginas + 1):
    
    html_tabela = elemento.get_attribute('outerHTML')
    tabela = pd.read_html(str(html_tabela))[0]
    lista_tabela_por_pagina.append(tabela)
    botao_avancar_pagina = driver.find_element("xpath", '//*[@id="nextPage"]')
    botao_avancar_pagina.click()
    
    
tabela_cadastro_etfs = pd.concat(lista_tabela_por_pagina)
formulario_de_voltar_pagina = driver.find_element("xpath", '//*[@id="goToPage"]')
formulario_de_voltar_pagina.clear()
formulario_de_voltar_pagina.send_keys("1")
formulario_de_voltar_pagina.send_keys(u'\ue007')
botao_mudar_pra_performance = driver.find_element("xpath", '/html/body/div[5]/section/div/div[3]/section/div/div/div/div/div[2]/section[2]/div[2]/ul/li[2]/span')
botao_mudar_pra_performance.click()
lista_tabela_por_pagina = []
elemento = driver.find_element("xpath", '//*[@id="finderTable"]')

for pagina in range(1, numero_paginas + 1):
    html_tabela = elemento.get_attribute('outerHTML')
    tabela = pd.read_html(str(html_tabela))[0]
    lista_tabela_por_pagina.append(tabela)
    botao_avancar_pagina = driver.find_element("xpath", '//*[@id="nextPage"]')
    driver.execute_script("arguments[0].click();", botao_avancar_pagina)
    
tabela_rentabilidade_etfs = pd.concat(lista_tabela_por_pagina)
tabela_rentabilidade_etfs
driver.quit()

tabela_cadastro_etfs = tabela_cadastro_etfs.set_index('Ticker')
tabela_rentabilidade_etfs = tabela_rentabilidade_etfs.set_index("Ticker")
tabela_rentabilidade_etfs = tabela_rentabilidade_etfs[['1 Year', '3 Years', '5 Years']]
tabela_rentabilidade_etfs = tabela_rentabilidade_etfs.replace("--", pd.NA)
tabela_rentabilidade_etfs = tabela_rentabilidade_etfs.dropna()
for coluna in tabela_rentabilidade_etfs.columns:
    tabela_rentabilidade_etfs[coluna] = tabela_rentabilidade_etfs[coluna].str.rstrip("%").astype(float)/100
base_final = tabela_cadastro_etfs.join(tabela_rentabilidade_etfs, how = "inner")
base_final = base_final[~base_final['Segment'].str.contains("Leveraged")]
base_final['rank_1_anos'] = base_final['1 Year'].rank(ascending = False)
base_final['rank_3_anos'] = base_final['3 Years'].rank(ascending = False)
base_final['rank_5_anos'] = base_final['5 Years'].rank(ascending = False)
base_final['rank_final'] = (base_final['rank_1_anos'] + 
                                  base_final['rank_3_anos'] + 
                                  base_final['rank_5_anos'])
base_final = base_final.sort_values(by = "rank_final")

print(base_final.head(20))
