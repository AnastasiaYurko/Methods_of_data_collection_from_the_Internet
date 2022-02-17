from pprint import pprint

from pymongo import MongoClient


from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

client = MongoClient('localhost', 27017)
db = client['mvideo']
collection = db.trands

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru/')

while True:
    try:
        button = driver.find_element(By.XPATH, "//div[@class='content']/span[contains(text(), 'В тренде')]/../..")
        button.click()
        for i in range(10):
            go_down = driver.find_element(By.TAG_NAME, 'html')
            go_down.send_keys(Keys.DOWN)
            i += 1
        break
    except:
        time.sleep(0.3)
        go_down = driver.find_element(By.TAG_NAME, 'html')
        go_down.send_keys(Keys.DOWN)

# while True:
#     try:
#         next = driver.find_element(By.XPATH, "//mvid-shelf-group//button[contains(@color, 'primary') and contains(@class, 'forward')]/..")
#         next.click()
#     except:
#         break

product_names = []
product_prices = []
product_rating = []

products = driver.find_elements(By.XPATH, "//mvid-shelf-group//div[@class='title']")
prices = driver.find_elements(By.XPATH, "//mvid-shelf-group//span[@class='price__main-value']")
stars = driver.find_elements(By.XPATH, "//mvid-shelf-group//span[@class='value ng-star-inserted']")

for product in products:
    product_names.append(product.text)

for price in prices:
    text_price = price.text
    product_prices.append(int(text_price.replace(' ', '')))

for star in stars:
    text_rating = star.text
    product_rating.append(float(text_rating.replace(',', '.')))

i = 0

for i in range(len(product_names)):
    product = {'Name': product_names[i],
               'Price': product_prices[i],
               'Rating': product_rating[i]}
    db.collection.insert_one(product)
    i += 1

for item in db.collection.find():
    pprint(item)

driver.quit()
