from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os
import json
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException
import tkinter as tk
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate('genius-bot-b8355-firebase-adminsdk-bookx-2d49ab4b27.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()


credit_button = '//*[contains(@class, "HeaderMetadata__ViewCredits")]'
ad_path = '//*[contains(@class, "bx-close-inside")]'
profile_img_path = '//*[contains(@class, "user_avatar profile_header-avatar")]'
total_list = []
data = []



def check_exists_if_view_more(id_num, element):
    try:
        driver.find_element(By.XPATH, id_num)
    except (NoSuchElementException, TimeoutException):
        return False
    return True

def print_dict_info(d):
    print(f"Name: {d['name']}")
    print("Songs:")
    for song in d['songs']:
        print(f"\tTitle: {song['title']}")
        print(f"\tArtist(s): {song['artist']}")
        print(f"\tLink: {song['link']}")
    print("Collaborators:")
    for collaborator in d['collaborators']:
        print(f"\t{collaborator}")


def get_top_songs(artist_name, driver):
    # Get the artist's page on Genius
    artist_name = artist_name.replace(".", "")
    artist_name = artist_name.replace("&", "and")
    url = f'https://genius.com/artists/{artist_name.replace(" ", "-")}'
    grid_songs = []    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "mini_card_grid-song")]')))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, profile_img_path)))
        grid_songs = driver.find_elements(By.XPATH, '//*[contains(@class, "mini_card_grid-song")]')
    except TimeoutException as e:
        get_top_songs(artist_name, driver)
    
    if check_exists_if_view_more(ad_path, driver):
        element = driver.find_element(By.XPATH, ad_path)
        driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, element)
    # Get the links to the artist's top 10 songs
    image_url = driver.find_element(By.XPATH, profile_img_path).value_of_css_property("background-image").lstrip('url("').rstrip('")')
    instagram_url = driver.find_elements(By.XPATH, '//*[contains(@class, "square_button--instagram")]').get_attribute('href')
    top_songs_links = []
    top_song_dict = []
    for link in grid_songs[:5]:
        yy = link.find_element(By.CLASS_NAME,'mini_card')
        top_songs_links.append(yy.get_attribute('href'))
        name = yy.find_element(By.CLASS_NAME, 'mini_card-title').text.strip()
        subtitle = yy.find_element(By.CLASS_NAME, 'mini_card-subtitle').text.strip()
        top_song_dict.append({'title': name, 'artist': subtitle, 'link': yy.get_attribute('href')})

    # Get the collaborators for each song
    collaborators = set()
    ztf = 0
    for song_link in top_songs_links:
        try:
            driver.get(song_link)
        except TimeoutException as e:
            driver.refresh()

        # Wait for the collaborators to load
        try:
            WebDriverWait(driver, 10).until(EC>presence_of_element_located((By.XPATH,'//*[contains(@class, "SizedImage__Image")]')))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[contains(@class, "SongInfo__Columns")]')))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, credit_button)))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[contains(@class, "SongHeaderdesktop__Title")]')))
        except:
            driver.refresh()

        title = driver.find_element(By.XPATH,'//*[contains(@class, "SongHeaderdesktop__Title")]').text.strip()
        artist = driver.find_element(By.XPATH,'//*[contains(@class, "SongHeaderdesktop__Artist")]').text.strip()
        song_image_url = driver.find_element(By.XPATH,'//*[contains(@class, "SizedImage__Image")]').get_attribute('src')
        top_song_dict[ztf]['image'] = song_image_url
        ztf += 1
        if check_exists_if_view_more('//*[contains(@class, "AppleMusicPlayer")]', driver):
            element = driver.find_element(By.XPATH, '//*[contains(@class, "AppleMusicPlayer")]')
            driver.execute_script("""
                var element = arguments[0];
                element.parentNode.removeChild(element);
                """, element)
        driver.find_element(By.XPATH, credit_button).click()
        time.sleep(0.9)
        credits = driver.find_element(By.XPATH,'//*[contains(@class, "SongInfo__Columns")]')
        credit_list = credits.find_elements(By.XPATH,'//*[contains(@class, "SongInfo__Credit")]')
        for c in credit_list:
            #print(c.get_attribute('class'))
            if c.find_element(By.TAG_NAME, 'div').text.strip() == "Produced By":
                song_collaborators = c.find_elements(By.TAG_NAME, 'span')
                for collaborator in song_collaborators:
                    xx = collaborator.find_element(By.TAG_NAME, 'a').text.strip()
                    if xx != artist_name and xx not in total_list:
                        collaborators.add(xx)
                        total_list.append(xx)
                break
    data.append({'name': artist_name, 'songs': top_song_dict, 'collaborators': collaborators, 'description': 'Empty for now. Come back soon for more', 'image_url': image_url, 'instagram_url': instagram_url[0]})
    return {'name': artist_name, 'songs': top_song_dict, 'collaborators': collaborators, 'description': 'Empty for now. Come back soon for more', 'image_url': image_url, 'instagram_url': instagram_url[0]}


# Initialize the Chrome driver
chrome_options = Options()
ser = Service(ChromeDriverManager().install())

uc.TARGET_VERSION = 112
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--dns-prefetch-disable")
#chrome_options.add_argument("start-maximized")
#chrome_options.add_argument("enable-automation")
print(os.environ)
chrome_options.binary_location = os.environ.get("CHROME_PATH")
driver = uc.Chrome(options=chrome_options, service=ser)
print("Driver Initialized")
driver.set_page_load_timeout(10)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


artist = sys.argv[1]
artist_ref = db.collection('artists').document(artist)

url = f"https://genius.com/search?q={artist}"
print(url)
print(driver)
tree = {}


try:
    driver.get(url)
except TimeoutException as e:
    print("Critical Error 12")
    time.sleep(2)
    driver.refresh()

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'mini_card')))
except:
    print("Critical Error 13")
    time.sleep(2)
    driver.refresh()

try:
    artist_link = driver.find_element(By.CLASS_NAME,'mini_card').get_attribute("href")
    artist_title = driver.find_element(By.CLASS_NAME,'mini_card').find_element(By.XPATH,'//*[contains(@class, "mini_card-title")]').text.strip()
    driver.get(artist_link)
except:
    print("Critical Error 11")
    time.sleep(2)
    driver.refresh()

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[contains(@class, "mini_card_grid-song")]')))
except:
    print("Critical Error 14")
    time.sleep(2)
    driver.refresh()


top_songs = driver.find_elements(By.XPATH,'//*[contains(@class, "mini_card_grid-song")]')
song_data = []
for song in top_songs[:7]:
    try:
        title = song.find_element(By.XPATH,'//*[contains(@class, "mini_card-title")]').text.strip()
        link = song.find_element(By.CLASS_NAME,'mini_card').get_attribute("href")
        song_data.append({"title": title, "link": link})
    except:
        print("Critical Error")
        driver.refresh()


# Get the collaborators for each song
songwriters = set()
for song_link in song_data:
    try:
        driver.get(song_link["link"])
    except TimeoutException as e:
        driver.refresh()
    # Wait for the collaborators to load
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[contains(@class, "SongInfo__Columns")]')))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, credit_button)))
    except TimeoutException as e:
        driver.refresh()
    if check_exists_if_view_more('//*[contains(@class, "AppleMusicPlayer")]', driver):
        element = driver.find_element(By.XPATH, '//*[contains(@class, "AppleMusicPlayer")]')
        driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, element)
    try:
        driver.find_element(By.XPATH, credit_button).click()
    except:
        print("DHDHD")
    time.sleep(0.9)
    credits = driver.find_element(By.XPATH,'//*[contains(@class, "SongInfo__Columns")]')
    credit_list = credits.find_elements(By.XPATH,'//*[contains(@class, "SongInfo__Credit")]')
    for c in credit_list:
        #print(c.get_attribute('class'))
        #print(c.find_element(By.TAG_NAME, 'div').text.strip())
        if c.find_element(By.TAG_NAME, 'div').text.strip() != "Featuring":
            song_collaborators = c.find_elements(By.TAG_NAME, 'span')
            for collaborator in song_collaborators:
                xx = collaborator.find_element(By.TAG_NAME, 'a').text.strip()
                if xx != artist_title and xx not in total_list:
                    songwriters.add(xx)
                    total_list.append(xx)
            break

data.append({'name': artist, 'songs': song_data, 'collaborators': songwriters, 'description': 'Empty for now. Come back soon for more'})
total_list.append(artist)

# Loop through each songwriter and get the collaborators for their top 10 songs
for songwriter in songwriters:
    collaborators = get_top_songs(songwriter, driver)
    collaborator_ref = artist_ref.collection('collaborators').document(collaborators['name'])
    collaborator_ref.set(collaborators)

print(data)
            
# Close the driver
driver.quit()

