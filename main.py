import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(filename='out.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def login_to_facebook(email, password):
    try:
        driver.get("https://www.facebook.com/")
        logging.info("Navigated to Facebook login page.")

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "email"))).send_keys(email)
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "pass"))).send_keys(password)

        WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.NAME, "login"))).click()
        logging.info("Successfully logged in.")

        WebDriverWait(driver, 10).until(ec.url_contains("facebook.com"))
    except Exception as e:
        logging.error(f"Error during login: {e}")
        driver.quit()


def get_profile_picture():
    try:

        driver.get("https://www.facebook.com/me")
        logging.info("Navigated to profile page.")


        profile_pic = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "image, img"))
        )


        src = profile_pic.get_attribute("xlink:href") or profile_pic.get_attribute("src")
        logging.info(f"Profile picture URL: {src}")
        return src
    except Exception as e:
        logging.error(f"Error while fetching profile picture: {e}")
        return None



def download_pic(profile_pic_url, save_path="profile_picture.jpg"):
    try:
        response = requests.get(profile_pic_url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            logging.info(f"Picture downloaded successfully and saved to {save_path}")
        else:
            logging.error(f"Failed to download picture. HTTP status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error while downloading picture: {e}")


def solve_recaptcha():
    logging.warning("CAPTCHA detected. Manual intervention required.")


def main():
    try:
        email = "test@gmail.com"
        password = "password"

        login_to_facebook(email, password)

        if "captcha" in driver.current_url:
            solve_recaptcha()

        profile_pic_url = get_profile_picture()
        if profile_pic_url:
            download_pic(profile_pic_url, save_path="profile_picture.jpg")
        else:
            logging.error("Failed to fetch profile picture.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
