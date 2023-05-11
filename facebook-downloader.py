import sys
import time
import os
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def main():
    webpage_url = get_webpage_url()
    driver = set_up_driver()
    get_webpage(driver, webpage_url)
    scroll_webpage(driver)
    images = get_images(driver)
    driver.close()
    save(images)


def set_up_driver():
    driver = webdriver.Firefox()
    return driver


def get_webpage_url():
    try:
        webpage_url = sys.argv[1]
    except IndexError:
        print("Please provide a valid URL.")
        sys.exit()
    return webpage_url


def get_webpage(driver, webpage_url):
    print("Getting webpage...")
    driver.get(webpage_url)
    accept_cookies(driver)
    global page_title   
    page_title = driver.find_element(By.CSS_SELECTOR, 'link[hreflang = "x-default"]').get_attribute("href").split("/")[-1]


def accept_cookies(driver):
    wait = WebDriverWait(driver, 20)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Consenti tutti i cookie"]'))
    )

    cookies = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Consenti tutti i cookie"]')
    driver.implicitly_wait(10)
    ActionChains(driver).move_to_element(cookies).click(cookies).perform()


def scroll_webpage(driver):
    print("Scrolling webpage...")

    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
    # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_images(driver):
    print("Collecting images...")
    elems = get_elems(driver)
    images = get_urls(driver, elems)
    return images


def get_elems(driver):
    elems_first_set = driver.find_elements(By.CSS_SELECTOR, "a[href*='.com/photo.php?fbid=']")
    elems_second_set = driver.find_elements(By.CSS_SELECTOR, "a[href*='photos/']")
    elems = elems_first_set + elems_second_set
    return elems


def get_urls(driver, elems):
    main_page = driver.current_window_handle
    images = []

    for count, elem in enumerate(elems):
        print("Collecting image #" + str(count + 1) + " of " + str(len(elems)) + "...")
        url = elem.get_attribute("href")
        driver.execute_script("window.open('{}')".format(url))
        wait = WebDriverWait(driver, 10)
        wait.until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[-1])
        wait = WebDriverWait(driver, 20)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[data-visualcompletion*='media-vc-image']"))
        )
        image_elem = driver.find_element(By.CSS_SELECTOR, "img[data-visualcompletion*='media-vc-image']")
        image_url = image_elem.get_attribute("src")
        image_title = image_url.split(".jpg")[0].split("/")[-1]
        image = {
            "url": image_url,
            "title": image_title
        }
        images.append(image)
        driver.close()
        driver.switch_to.window(main_page)
    
    return images


def save(images):
    print("Downloading images...")
    for count, image in enumerate(images):
        print("Downloading image #" + str(count + 1) + " of " + str(len(images)) + "...")
        facebook_folder = os.path.join(os.getcwd(), "facebook")
        try:
            os.makedirs(facebook_folder)
        except OSError:
            pass
        page_folder = os.path.join(facebook_folder, page_title)
        try:
            os.makedirs(page_folder)
        except OSError:
            pass
        out_path = os.path.join(page_folder, image["title"] + ".jpg")
        urllib.request.urlretrieve(image["url"], out_path)
    print("Done.")


if __name__ == "__main__":
    main()
