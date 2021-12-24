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
from  utils.enums import Available
from db_functions import insert
import time 
import json
import logging

PARSING_EXCEPTION = "a problem happened while scraping data"
YES = "yes"
NO = "no"

# create logger
logger = logging.getLogger('scrape_cards.py')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

# get list of graphcis cards
def getCards():
    page_count = 1
    url = "https://www.bestbuy.com/site/searchpage.jsp?cp="+str(page_count)+"&id=pcat17071&st=graphics+cards"  
    options = Options()
    # options.add_argument("start-maximized")
    # options.add_argument("disable-infobars")
    # options.add_argument("--disable-extensions")
    #uncomment below when done debugging  
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--headless");
    options.add_argument('--no-proxy-server')
    options.add_argument("--proxy-server='direct://'");
    options.add_argument("--proxy-bypass-list=*");
    driver = webdriver.Chrome(chrome_options=options,executable_path='./chromedriver')
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
    logger.info("page count: %s ", str(page_count))
    # driver.quit()
    #need to return as a dictionary for pydantic model parsing
    dictReturn ={}
    json_object = []
    error = None
    for x in range(page_count):
        logger.info("loading page: %s",  str(x +1))
        # driver = webdriver.Chrome(chrome_options=options,executable_path='./chromedriver')
        url = "https://www.bestbuy.com/site/searchpage.jsp?cp="+str(x +1)+"&id=pcat17071&st=graphics+cards"
        driver.get(url)
        driver.implicitly_wait(4)
        page_html = driver.page_source
        try:
            # html parsing
            page_soup = soup(page_html, "html.parser")
            #get all items for sale
            cards = page_soup.findAll("li", {"class": "sku-item"})
            logger.info("scraping page ...")
            # print("CARDS :" +str(cards))
            for card in cards:
                card_dictionary ={}
                sku_values = card.findAll("span", {"class": ["sku-value"]})
                header = card.find("h4", {"class": ["sku-header"]})
                if header is not None:      
                    card_dictionary["card_name"] =header.a.text
                    # logger.info("card_name : %s",str(header.a.text))
                else:
                    logger.info("no card name found")
                sku_index = len(sku_values) -1
                if sku_values[sku_index] is not None: 
                    card_dictionary["sku_value"] =sku_values[sku_index].text
                else:
                    logger.info("no sku value for above card")            
                buy_button = card.find("div", {"class": ["fulfillment-add-to-cart-button"]})
                button_text = buy_button.div.div.button
                if button_text is not None:
                    button_text = buy_button.div.div.button.text
                else:
                    button_text = buy_button.div.div.a.text
                card_dictionary["available"] = NO
                if button_text is not None:
                    #default to some text in case we dont handle some new string bestbuy adds
                    card_dictionary["available"] = button_text
                if button_text == "Unavailable Nearby":
                    card_dictionary["available"] =  NO
                if button_text == "Add to Cart":
                    card_dictionary["available"] = YES
                if button_text == "Sold Out":
                    card_dictionary["available"] = NO

                json_object.append(card_dictionary)
                driver.implicitly_wait(4)
        except (Exception) as error:
            #catch any exception and return some information with the 500 status
            logger.error(error)
            logger.error(PARSING_EXCEPTION)
            raise HTTPException(status_code=500, detail=PARSING_EXCEPTION) 

        # driver.quit()
    dictReturn["cards"] = json_object
    app_json = json.dumps(dictReturn)
    app_json = json.loads(app_json)

    # insert data in to table
    insert(app_json)
    # logger.info(app_json)

    logger.info("number of cards scraped: %s", str(len(json_object)))
  
    return app_json

