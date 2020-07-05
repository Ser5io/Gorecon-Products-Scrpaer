from datetime import datetime
from random import randint

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def getCategoriesURL(link):
    driver.get(link)

    CATEGORIES_CLASSNAME = "product-categories"
    WebDriverWait(driver, pageLoadDelay).until(EC.presence_of_element_located((By.CLASS_NAME, CATEGORIES_CLASSNAME)))

    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")

    gallery = soup.find('ul', attrs={'class': CATEGORIES_CLASSNAME})
    items = gallery.find_all('li')
    categoriesURL = []
    for item in items:
        if len(item['class']) > 2:
            continue
        elif item.contents[2].text == "(0)":
            continue

        categoriesURL.append(item.contents[0]['href'])

    return categoriesURL


def getProductsURL(link):
    PRODUCTS_CLASSNAME = "products"
    NEXT_CLASSNAME = "next"

    productsURL = []
    hasNextPage = True
    while hasNextPage:
        driver.get(link)
        WebDriverWait(driver, pageLoadDelay).until(EC.presence_of_element_located((By.CLASS_NAME, PRODUCTS_CLASSNAME)))

        content = driver.page_source
        soup = BeautifulSoup(content, features="lxml")

        gallery = soup.find('div', attrs={'class': PRODUCTS_CLASSNAME})
        items = gallery.find_all('a')
        for item in items:
            if "button" in item['class']:
                continue

            productsURL.append(item['href'])

        nextPageLink = soup.find('a', attrs={'class': NEXT_CLASSNAME})
        if nextPageLink:
            link = nextPageLink['href']
        else:
            hasNextPage = False

    return productsURL


def getProductImagesURL(link):
    driver.get(link)

    PRODUCT_CLASSNAME = "woocommerce-product-gallery__wrapper"
    WebDriverWait(driver, pageLoadDelay).until(EC.presence_of_element_located((By.CLASS_NAME, PRODUCT_CLASSNAME)))

    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")

    gallery = soup.find('figure', attrs={'class': PRODUCT_CLASSNAME})
    images = gallery.find_all('a')
    productImagesURL = []
    for image in images:
        productImagesURL.append(image['href'])

    return productImagesURL


try:
    pageLoadDelay = 10
    CATEGORIES_LINK = "https://gorecon.com/product"

    CHROME_PATH = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    CHROMEDRIVER_PATH = 'C:\src\chromedriver.exe'
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # comment this line if you want to see the scraper working
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.binary_location = CHROME_PATH

    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)

    csv = {"url": [], "Main-Image": []}
    for i in range(1, 10):
        csv["Add-Image-{i}".format(i=i)] = []
    keys = list(csv.keys())

    categories = getCategoriesURL(CATEGORIES_LINK)
    # categories = [categories[0]]  # Uncomment this line to test only the first category
    for category in categories:
        products = getProductsURL(category)
        for product in products:
            csv['url'].append(product)
            productImages = getProductImagesURL(product)
            for index, image in enumerate(productImages):
                if not index:
                    csv["Main-Image"].append(image)
                else:
                    csv["Add-Image-{i}".format(i=index)].append(image)
            for i in range(1, len(keys)):
                if len(csv[keys[i]]) < len(csv[keys[0]]):
                    csv[keys[i]].append("")

finally:
    driver.quit()
    if len(csv[keys[0]]) > 1:
        df = pd.DataFrame(csv)
        try:
            df.to_csv('products_{datetime}.csv'.format(datetime=datetime.today().strftime("%d-%m-%Y--%H-%M-%S")),
                      index=False, encoding='utf-8')
        except PermissionError:
            fileName = 'products{randomNumber}.csv'.format(randomNumber=randint(1, 100000))
            df.to_csv(fileName, index=False, encoding='utf-8')
            print('products.csv file was still open so we saved it as ', fileName)

    else:
        print('Nothing to save')

    print("Done")
