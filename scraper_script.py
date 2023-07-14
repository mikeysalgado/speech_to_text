import time
import requests
from splice_audio import split_audio_by_time_stamps
from bs4 import BeautifulSoup
from pydub import AudioSegment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import os

# Initial Setup
root_dirname = os.path.dirname(os.path.abspath(__file__))
options = Options()
options.add_experimental_option("prefs", {
  "download.default_directory": root_dirname+'\\video_files'
  })
print('Root directory', root_dirname)
print("Will download the audio to:", root_dirname+'\\video_files')
print("Will download the transcript to:", root_dirname+'\\transcript')

# url = 'https://www.ted.com/talks/albert_fox_cahn_the_shift_we_need_to_stop_mass_surveillance?language=en'
# url = 'https://www.ted.com/talks/grady_booch_don_t_fear_superintelligent_ai/language=en'

# Setting element paths

# Set up the driver
# chrome_service = Service('C:/Users/salgadom/Documents/CS 4980 003/Project/chromedriver.exe')
# chrome_service.start()
# driver = webdriver.Chrome(service=chrome_service, options=options)

# Navigate to the TED Talk page
# driver.get(url)

# TODO - Replace with local path location if needed
# Setting AudioSegment .exe Paths
AudioSegment.ffmpeg_path = "./ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
AudioSegment.ffprobe_path = "./ffmpeg-6.0-essentials_build/bin/ffprobe.exe"

class MissingDownloadException(Exception):
    "Raised when the chrome downloads list is empty"
    pass


def grab_ted_talk_urls(num_pages=10, sort="popular"):
    """
    Will grab the urls from n number of Ted Talk Pages
    :param num_pages:
        num_pages::int
            Number of pages to scrape
    :return:
        urls::list(str)
            A list of string urls
    """
    urls = []
    for page_num in range(1,num_pages+1):

        res = requests.get("https://www.ted.com/talks?sort=" + sort + "&page=" + str(page_num))

        soup = BeautifulSoup(res.text, features="lxml")
        e = soup.select("div.container.results div.col")

        if len(e) == 0:    break  # No more videos.

        for u in e:
            urls.append("https://www.ted.com" + u.select("div.media__image a.ga-link")[0].get("href"))
    return urls


def elementHasClass(element, active):
    return active in element.get_attribute("class")


def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items;
        if (items.length === 0) return null;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.fileUrl || e.file_url);
        """)
    # return driver.execute_script("""
    #     var items = document.querySelector('downloads-manager')
    #         .shadowRoot.getElementById('downloadsList').items;
    #     if (items.every(e => e.state === "COMPLETE"))
    #         return items.map(e => e.fileUrl || e.file_url);
    #     """)


def extract_process(url):
    try:
        driver = selenium_setup(url)

        # Extracting .mp4 file
        extract_video(driver)

        # Extracting transcript
        paragraphs, paths = extract_transcript(driver)
        if paragraphs is None:
            raise MissingDownloadException
        
        print(f"Converting {paths[0]} to MP3 and splicing by {len(paragraphs)} timestamps...")
        split_audio_by_time_stamps(paragraphs, paths[0], 'output_files')
        print("Completed MP3 conversion.")
    except MissingDownloadException:
        print(f"No download found on {url}, skipping file")
    except Exception as e:
        print(f"An error occurred: {e}")
        # root_dirname = os.path.dirname(os.path.abspath(__file__))

    video_files_dir = os.path.join(root_dirname, 'video_files')

    # Delete all mp4 files in the video_files directory
    for file_name in os.listdir(video_files_dir):
        if file_name.endswith('.mp4'):
            os.remove(os.path.join(video_files_dir, file_name))
        if file_name.endswith('.crdownload'):
            os.remove(os.path.join(video_files_dir, file_name))
    with open('completed_urls.txt', 'a') as f:
        f.write(url + '\n')


    driver.quit()
    print(f"Finished {paths[0]}")


# TODO - Change Chromedriver .exe path location
def selenium_setup(url):
        # Setup
    chrome_service = Service('C:/Users/salgadom/Documents/CS 4980 003/Project/chromedriver.exe')
    chrome_service.start()

    # Navigate to the TED Talk page
    driver = webdriver.Chrome(service=chrome_service, options=options)
    driver.get(url)

    # set up the URL for the TED Talk transcript page
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    # retrieve the TED Talk transcript page
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Wait for the other element to become invisible
    other_element = WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.XPATH, '//div[@class="w-full"]')))
    return driver


def extract_transcript(driver):
    print("Extracting transcript...")
    # Grabbing Transcript element paths
    read_transcript_button_path = '//*[@id="maincontent"]/div/div/div/div/div[2]/div[1]/div[4]/button'
    transcript_container_path = '#maincontent > div > div > div > aside > div.pt-6.lg\:pl-8.lg\:pr-2.xl\:pl-12.xl\:pr-4.css-1fh91ol.e5j128k1 > div.open.css-1b8n8c1.e5j128k3 > div > div > div.mx-auto.mb-10.w-full > div:nth-child(3)'
    read_transcript_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, read_transcript_button_path)))
    read_transcript_button.click()
    time.sleep(1)
    transcript_container = driver.find_elements(By.CSS_SELECTOR, transcript_container_path)


    paragraphs = []
    for tc_child in transcript_container:
        paragraph_div = tc_child.find_elements(By.CSS_SELECTOR, 'div')
        for paragraph_entry in paragraph_div:
            paragraph = paragraph_entry.text.split('\n')
            # print(paragraph)
            if len(paragraph) > 1:
                print(paragraph)
                paragraphs.append(paragraph)
    time.sleep(6)
    print("Extracted transcript.")
    
    print("Waiting for download to finish...")
    # waits for all the files to be completed and returns the paths
    paths = WebDriverWait(driver, 120, 1).until(every_downloads_chrome)
    if paths is None:
        print('No downloads listed, skipping file.')
        return None, None
    print("Finished downloading.")
    # Removes the file path and file extension:
    # e.g.'file:///C:/Users/dangn/Downloads/2022u-albert-fox-cahn-003-5000k (1).mp4' -> '2022u-albert-fox-cahn-003-5000k'
    print("Saving to CSV...")
    file_name = re.sub(r"\(\d\)", r"", paths[0].split('/')[-1].split('.')[0].rstrip(' .*').replace('%20', '').replace(' ', ''))
    pd.DataFrame(paragraphs, columns=['timestamp', 'text']).to_csv(f'{root_dirname}\\transcript\\{file_name}.csv', index=False)
    print("Transcript saved to CSV.")
    return paragraphs, paths


def extract_video(driver):
    print("Extracting video...")
    share_button_path = '//*[@id="maincontent"]/div/div/div/div/div[2]/div[1]/div[4]/div/div[2]/button/div/div'
    audio_button_path = '/html/body/reach-portal[2]/div[3]/div/div/div[1]/div/div/div/div/div/div/div/div[2]/div[2]/div[2]/a[1]/div[1]'
    share_exit_button_path = '/html/body/reach-portal[2]/div[3]/div/div/div[1]/div/div/div/div/div/div/button'
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
    print("Successfully extracted video")


if __name__== '__main__':
    # Sorts include popular, newest, oldest, and relevance
    urls = grab_ted_talk_urls(num_pages=50, sort="newest")
    print(f"URLs to scrape ({len(urls)}):", urls)
    for url in urls:
        try:
            with open('completed_urls.txt', 'r') as file:
                contents = file.read()
                if url not in contents:
                    print(f"Scraping {url}")
                    extract_process(url)
                else:
                    print(f"Already scraped this url ({url}), skipping to next")
        except:
            print("Error scraping ", url)
    print("Finished with list of URLs")
