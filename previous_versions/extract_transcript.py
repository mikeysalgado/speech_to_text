import time
import requests
from splice_audio import split_audio_by_time_stamps
from bs4 import BeautifulSoup
from pydub import AudioSegment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# url = 'https://www.ted.com/talks/albert_fox_cahn_the_shift_we_need_to_stop_mass_surveillance?language=en'
url = 'https://www.ted.com/talks/grady_booch_don_t_fear_superintelligent_ai/transcript?language=en'
# Set up the driver
chrome_service = Service('C:/Users/salgadom/Documents/CS 4980 003/Project/chromedriver.exe')
chrome_service.start()
driver = webdriver.Chrome(service=chrome_service)

# Navigate to the TED Talk page
driver.get(url)


AudioSegment.ffmpeg_path = "./ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
AudioSegment.ffprobe_path = "./ffmpeg-6.0-essentials_build/bin/ffprobe.exe"

def extract_transcript():
    # Wait for the other element to become invisible
    other_element = WebDriverWait(driver, 25).until(
        EC.invisibility_of_element_located(
            (By.XPATH, '//div[@class="w-full"]')
        )
    )

    time.sleep(1)

    # # Click the button
    # read_transcript_button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable(
    #         (By.XPATH, '//*[@id="maincontent"]/div/div/div/div/div[2]/div[1]/div[4]/button')
    #     )
    # )
    # read_transcript_button.click()

    time.sleep(1)
    transcript_container = driver.find_elements(
        By.CSS_SELECTOR, '#maincontent > div > div > div > aside > div.pt-6.lg\:pl-8.lg\:pr-2.xl\:pl-12.xl\:pr-4.css-1fh91ol.e5j128k1 > div.open.css-1b8n8c1.e5j128k3 > div > div > div.mx-auto.mb-10.w-full > div:nth-child(3)'
    )

    time.sleep(1)
    paragraphs = []
    for tc_child in transcript_container:
        paragraph_div = tc_child.find_elements(By.CSS_SELECTOR, 'div')
        for paragraph_entry in paragraph_div:
            paragraph = paragraph_entry.text.split('\n')
            if len(paragraph) > 1:
                print(paragraph)
                print()
                paragraphs.append(paragraph)        

    return paragraphs

def extract_audio(paragraphs, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    audio_urls = []
    sentence_times = []
    for span in soup.select("span.t"):
        start_time, end_time = span["data-time"].split(";")
        sentence_times.append((float(start_time), float(end_time)))
        audio_url = span.find_next_sibling("a")["href"]
        audio_urls.append(audio_url)

# Call the extract_transcript function
paragraphs = extract_transcript()
# print(paragraphs)

audio_file = AudioSegment.from_file('./audio_files/2016s-grady-booch-009-5000k.mp3')

split_audio_by_time_stamps(paragraphs, audio_file, 'output_files')
# extract_audio.(paragraphs, url)
# Close the driver
driver.quit()
