import getpass
import os
import random
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from comment_list import comment_list
from utils import login_from_fb, login_from_insta

# Input for login method
login_mode = input("If you want to login via Facebook press y/Y else login via Instagram credentials by pressing n/N: ")
login_method = 'facebook' if login_mode.lower() == 'y' else 'instagram'

# Get the user's username and password
username = input(f"Enter your {login_method.upper()} username: ")
password = getpass.getpass(f"Enter your {login_method.upper()} password: ")
password_match = getpass.getpass(f"Enter your {login_method.upper()} password again: ")

# Keep getting the password until two consecutive inputs do NOT match
while password != password_match:
    password = getpass.getpass("Your password did NOT match. Please enter your password again: ")
    password_match = getpass.getpass("Please enter your password again: ")

# Creating folder with the name of the person you want to download pictures of
friend_username = input("Enter the Instagram username of the person you want to like and download all the photos of: ")
folder_name = friend_username

# Check if the directory with the name already exists
if os.path.exists(folder_name):
    folder_name = input(f"The folder with the name '{friend_username}' already exists. "
                        "Enter the name of folder you want to save all photos to: ")
    while os.path.exists(folder_name):
        folder_name = input(f"The folder with the name '{folder_name}' also exists. "
                            "Enter the name of folder you want to save all photos to: ")

os.makedirs(folder_name, exist_ok=True)

# Initialize ChromeDriver
service = ChromeService(executable_path=ChromeDriverManager().install())
browser_obj = webdriver.Chrome(service=service)

# Setting implicit wait to 10 seconds
browser_obj.implicitly_wait(10)

browser_obj.get('http://instagram.com')

print(f"Login method: {login_method}")

# Calling the login function depending upon the user preference of login via FB or Insta
if login_method == "facebook":
    login_from_fb(browser_obj, username, password)
else:
    login_from_insta(browser_obj, username, password)

# Creating a delay for login to happen properly
time.sleep(5)

# Going to the profile of the specified user
browser_obj.get(f'http://instagram.com/{friend_username}/')

# Loading more pictures in their profile
try:
    load_more = WebDriverWait(browser_obj, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Load more")]'))
    )
    load_more.click()
except Exception as e:
    print(f"Error finding or clicking the 'Load more' button: {e}")

last_height = browser_obj.execute_script("return document.body.scrollHeight")
while True:
    browser_obj.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    new_height = browser_obj.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

browser_obj.execute_script("window.scrollTo(0, 0);")

# Get all image and video elements
def do(browser_obj):
    # Scroll down to load all posts
    browser_obj.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Find all post elements
    posts = browser_obj.find_elements(By.XPATH, '//article//div[@role="presentation"]//div[@role="presentation"]')
    
    for post in posts:
        try:
            # Click the post to open it
            post.click()
            time.sleep(2)

            # Try to retrieve video
            try:
                video_elem = WebDriverWait(browser_obj, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//article//video'))
                )
                src = video_elem.get_attribute('src')
                if src:
                    filename = os.path.join(folder_name, src.split('/')[-1])
                    print(f"Downloading video from URL: {src} to {filename}")
                    urllib.request.urlretrieve(src, filename)
                else:
                    print("No video URL found.")
            except Exception as e:
                print(f"Error retrieving video source: {e}")

                # If video not found, try to get image
                try:
                    img_elem = WebDriverWait(browser_obj, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//article//img'))
                    )
                    src = img_elem.get_attribute('src')
                    if src:
                        filename = os.path.join(folder_name, src.split('/')[-1])
                        print(f"Downloading image from URL: {src} to {filename}")
                        urllib.request.urlretrieve(src, filename)
                    else:
                        print("No image URL found.")
                except Exception as e:
                    print(f"Error retrieving image source: {e}")

            # Like the post
            try:
                like_button = WebDriverWait(browser_obj, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//article//span[@aria-label="Like"]'))
                )
                like_button.click()
            except Exception as e:
                print(f"Error liking the post: {e}")

            # Comment on post
            if comment_counter == 5:
                try:
                    text_area = WebDriverWait(browser_obj, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//form//textarea'))
                    )
                    comment = random.choice(comment_list[0])
                    for i in range(1, len(comment_list)):
                        comment += ' ' + random.choice(comment_list[i])
                    print(f"Commenting: {comment}")
                    text_area.send_keys(comment + Keys.RETURN)
                    comment_counter = 0
                except Exception as e:
                    print(f"Error commenting on the post: {e}")

            comment_counter += 1

            # Close the image
            try:
                close_button = WebDriverWait(browser_obj, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Close")]'))
                )
                close_button.click()
            except Exception as e:
                print(f"Error closing the image: {e}")

        except Exception as e:
            print(f"Error processing post: {e}")

do(browser_obj)
browser_obj.quit()
