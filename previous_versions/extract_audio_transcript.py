import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import re
import os

root_dirname = os.path.dirname(os.path.abspath(__file__))
options = Options()
options.add_experimental_option("prefs", {
  "download.default_directory": root_dirname+'\\audio'
  })
print('Root directory', root_dirname)
print("Will download the audio to:", root_dirname+'\\audio')
print("Will download the transcript to:", root_dirname+'\\transcript')

url = 'https://www.ted.com/talks/albert_fox_cahn_the_shift_we_need_to_stop_mass_surveillance?language=en'

# Grabbing Transcript element paths
read_transcript_button_path = '//*[@id="maincontent"]/div/div/div/div/div[2]/div[1]/div[4]/button'
transcript_container_path = '#maincontent > div > div > div > aside > div.pt-6.lg\:pl-8.lg\:pr-2.xl\:pl-12.xl\:pr-4.css-1fh91ol.e5j128k1 > div.open.css-1b8n8c1.e5j128k3 > div > div > div.mx-auto.mb-10.w-full > div:nth-child(3)'

# Grabbing MP4 element paths
share_button_path = '//*[@id="maincontent"]/div/div/div/div/div[2]/div[1]/div[4]/div/div[2]/button/div/div'
audio_button_path = '/html/body/reach-portal[2]/div[3]/div/div/div[1]/div/div/div/div/div/div/div/div[2]/div[2]/div[2]/a[1]/div[1]'
share_exit_button_path = '/html/body/reach-portal[2]/div[3]/div/div/div[1]/div/div/div/div/div/div/button'

# Set up the driver
chrome_service = Service('C:/Users/salgadom/Documents/CS 4980 003/Project/chromedriver.exe', options=options)
chrome_service.start()

def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.fileUrl || e.file_url);
        """)


driver = webdriver.Chrome(service=chrome_service, options=options)

# Navigate to the TED Talk page
driver.get(url)

# set up the URL for the TED Talk transcript page
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

# retrieve the TED Talk transcript page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Wait for the other element to become invisible
other_element = WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.XPATH, '//div[@class="w-full"]')))

# Grabs audio
# Click Share button then download the mp4 file
share_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, share_button_path)))
share_button.click()
time.sleep(2)
audio_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, audio_button_path)))
audio_button.click()
time.sleep(1)
share_exit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, share_exit_button_path)))
share_exit_button.click()

# Grabs transcript
# Click the read transcript button then grab the transcript
read_transcript_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, read_transcript_button_path)))
read_transcript_button.click()
time.sleep(1)
transcript_container = driver.find_elements(By.CSS_SELECTOR, transcript_container_path)


paragraphs = []
for tc_child in transcript_container:
    paragraph_div = tc_child.find_elements(By.CSS_SELECTOR, 'div')
    for paragraph_entry in paragraph_div:
        paragraph = paragraph_entry.text.split('\n')
        if len(paragraph) > 1:
            paragraphs.append(paragraph)
time.sleep(6)


# waits for all the files to be completed and returns the paths
paths = WebDriverWait(driver, 120, 1).until(every_downloads_chrome)

# Removes the file path and file extension:
# e.g.'file:///C:/Users/dangn/Downloads/2022u-albert-fox-cahn-003-5000k (1).mp4' -> '2022u-albert-fox-cahn-003-5000k'
file_name = re.sub(r"\(\d\)", r"", paths[0].split('/')[-1].split('.')[0].rstrip(' .*').replace(' ', ''))
pd.DataFrame(paragraphs, columns=['timestamp', 'text']).to_csv(f'{root_dirname}\\transcript\\{file_name}.csv', index=False)
print("DONE")



# Close the driver
driver.quit()
