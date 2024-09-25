from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

def get_login_page(login_type, browser_obj):
    if login_type == 'facebook':
        browser_obj.get('https://www.facebook.com/login')
        try:
            log_in = WebDriverWait(browser_obj, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[@name="login"]'))
            )
            log_in.click()
        except Exception as e:
            print(f"Error finding or clicking the Facebook login button: {e}")

    elif login_type == 'instagram':
        browser_obj.get('https://www.instagram.com/accounts/login/')
        try:
            log_in = WebDriverWait(browser_obj, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[@type="submit"]'))
            )
            log_in.click()
        except Exception as e:
            print(f"Error finding or clicking the Instagram login button: {e}")

def login_from_fb(browser_obj, username, password):
    get_login_page('facebook', browser_obj)
    try:
        email_field = WebDriverWait(browser_obj, 10).until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        password_field = WebDriverWait(browser_obj, 10).until(
            EC.presence_of_element_located((By.ID, 'pass'))
        )
        email_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"Error during Facebook login: {e}")

def login_from_insta(browser_obj, username, password):
    get_login_page('instagram', browser_obj)
    try:
        username_field = WebDriverWait(browser_obj, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password_field = WebDriverWait(browser_obj, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"Error during Instagram login: {e}")
