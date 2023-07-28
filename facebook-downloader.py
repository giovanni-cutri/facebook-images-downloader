import argparse
import time
import os
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException


def main():
    args = parse_arguments()
    urls = []
    titles = []
    if args.album:
        album_driver = set_up_driver()
        url = args.url.strip("/") + "/photos_albums"
        get_webpage(album_driver, url)
        scroll_webpage(album_driver)
        urls, titles = get_albums(album_driver)
        album_driver.quit()
    else:
        url = args.url.strip("/") + "/photos"
        urls.append(url)
    for album_number, url in enumerate(urls):
        driver = set_up_driver()
        get_webpage(driver, url)
        scroll_webpage(driver)
        images = get_images(driver, album_number)
        driver.close()
        save(images, album_number, titles)
        driver.quit()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="the URL of the Facebook page")
    parser.add_argument("-a", "--album", help="download images in different folders corresponding to the albums they are located in", action="store_true")
    args = parser.parse_args()
    return args


def set_up_driver():
    driver = webdriver.Firefox()
    return driver


def get_webpage(driver, url):
    print("Getting webpage...")
    driver.get(url)
    accept_cookies(driver)
    close_login(driver)
    global page_title
    page_title = driver.find_element(By.CSS_SELECTOR, 'h1').get_attribute("innerHTML")


def accept_cookies(driver):
    wait = WebDriverWait(driver, 20)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Consenti tutti i cookie"]'))
    )

    cookies = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Consenti tutti i cookie"]')
    driver.implicitly_wait(10)
    ActionChains(driver).move_to_element(cookies).click(cookies).perform()


def close_login(driver):

    try:
        wait = WebDriverWait(driver, 20)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Chiudi"]'))
        )

        login = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Chiudi"]')
        driver.implicitly_wait(10)
        ActionChains(driver).move_to_element(login).click(login).perform()
    except TimeoutException:
        pass


def scroll_webpage(driver):
    print("Scrolling webpage...")

    SCROLL_PAUSE_TIME = 5

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


def get_albums(album_driver):
    print("Collecting albums...")
    album_elems = album_driver.find_elements(By.CSS_SELECTOR, "a[href*='.com/media/set/']")
    album_titles_elems = album_driver.find_elements(By.CSS_SELECTOR, "a[href*='.com/media/set/'] span")
    albums = []
    album_titles = []
    for album_elem in album_elems:
        album = album_elem.get_attribute("href")
        albums.append(album)
    for album_title_elem in album_titles_elems[::2]:
        album_title = album_title_elem.get_attribute("innerHTML")
        album_titles.append(album_title)
    return albums, album_titles


def get_images(driver, album_number):
    print(f"\nCollecting images of album #{album_number + 1}...")
    elems = get_image_elems(driver)
    images = get_urls(driver, elems)
    return images


def get_image_elems(driver):
    elems_first_set = driver.find_elements(By.CSS_SELECTOR, "a[href*='.com/photo.php?fbid=']")
    elems_second_set = driver.find_elements(By.CSS_SELECTOR, "a[href*='photos/']")
    elems_third_set = driver.find_elements(By.CSS_SELECTOR, "a[href*='/photo/?fbid=']")[2:]   # the first two photos are the profile pictures
    elems = elems_first_set + elems_second_set + elems_third_set
    return elems


def get_urls(driver, elems):
    main_page = driver.current_window_handle
    images = []

    for count, elem in enumerate(elems):
        print("Collecting image #" + str(count + 1) + " of " + str(len(elems)) + "...")
        url = elem.get_attribute("href")
        if not "facebook.com" in url:
            url = "https://www.facebook.com" + url
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
        image_title = image_url.split("?")[0].split("/")[-1][:-4]
        image = {
            "url": image_url,
            "title": image_title
        }
        images.append(image)
        driver.close()
        driver.switch_to.window(main_page)
    
    return images


def save(images, album_number, titles):
    print(f"\nDownloading images of album #{album_number + 1}...")
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
        if titles:
            album_folder = os.path.join(page_folder, titles[album_number])
            try:
                os.makedirs(album_folder)
            except OSError:
                pass
            out_path = os.path.join(album_folder, image["title"] + ".jpg")
        else:
            out_path = os.path.join(page_folder, image["title"] + ".jpg")
        urllib.request.urlretrieve(image["url"], out_path)
    print("Done.")


if __name__ == "__main__":
    main()
