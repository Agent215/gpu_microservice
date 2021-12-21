from urllib.request import urlopen
#get the beautifulSoup module and name as soup
from fastapi import FastAPI, HTTPException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
from db_functions import insert
import time 
import json

PARSING_EXCEPTION = "a problem happened while scraping data"

CHROME_DRIVER_PATH =r'C:\Users\brahm\Downloads\chromedriver_win32\chromedriver.exe'

# get list of graphcis cards
def getCards():
    page_count = 1
    url = "https://www.bestbuy.com/site/searchpage.jsp?cp="+str(page_count)+"&id=pcat17071&st=graphics+cards"  
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    #uncomment below when done debugging  
    # options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options,executable_path=CHROME_DRIVER_PATH)
    driver.get(url)
    driver.implicitly_wait(3)
    
    # get the current pages html
    page_html = driver.page_source
    # # html parsing
    page_soup = soup(page_html, "html.parser")
    # get all items for sale
    
    paging_list = page_soup.find("ol", {"class": "paging-list"})
    page_count = paging_list.findAll("li", {"class": "page-item"})
    page_count = int(page_count[4].text)
    print("page count: " + str(page_count))
    driver.quit()
    #need to return as a dictionary for pydantic model parsing
    dictReturn ={}
    json_object = []
    error = None
    for x in range(page_count):
        print("page: " + str(x +1))
        driver = webdriver.Chrome(chrome_options=options,executable_path=CHROME_DRIVER_PATH)
        url = "https://www.bestbuy.com/site/searchpage.jsp?cp="+str(x +1)+"&id=pcat17071&st=graphics+cards"
        driver.get(url)
        driver.implicitly_wait(4)
        page_html = driver.page_source
        try:
            # html parsing
            page_soup = soup(page_html, "html.parser")
            #get all items for sale
            cards = page_soup.findAll("li", {"class": "sku-item"})
            # print("CARDS :" +str(cards))
            for card in cards:
                card_dictionary ={}
                sku_values = card.findAll("span", {"class": ["sku-value"]})
                header = card.find("h4", {"class": ["sku-header"]}) 
                card_dictionary["card_name"] =header.a.text
                print(str(header.a.text))
                sku_index = len(sku_values) -1
                if sku_values[sku_index] is not None: 
                    card_dictionary["sku_value"] =sku_values[sku_index].text            
                buy_button = card.find("div", {"class": ["fulfillment-add-to-cart-button"]})
                button_text = buy_button.div.div.button.text
                card_dictionary["available"] = "No"
                if button_text is not None:
                    #default to some text in case we dont handle some new string bestbuy adds
                    card_dictionary["available"] = button_text
                if button_text == "Unavailable Nearby":
                    card_dictionary["available"] = "No"
                if button_text == "Add to Cart":
                    card_dictionary["available"] = "Yes"
                if button_text == "Sold Out":
                    card_dictionary["available"] = "No"

                json_object.append(card_dictionary)
                driver.implicitly_wait(4)
        except (Exception) as error:
            #catch any exception and return some information with the 500 status
            print(error)
            print(PARSING_EXCEPTION)
            raise HTTPException(status_code=500, detail=PARSING_EXCEPTION) 

        driver.quit()
    dictReturn["cards"] = json_object
    app_json = json.dumps(dictReturn)
    app_json = json.loads(app_json)

    insert(app_json)
    print(app_json)
    print(len(cards))
  
    return app_json

