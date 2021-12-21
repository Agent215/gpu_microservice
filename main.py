from typing import Optional
from pydantic import BaseModel ,json
from fastapi import FastAPI, HTTPException
from scrape_cards import getCards
from db_functions import get_all_cards, get_card,get_card_available
from typing import List
from model import Card,CardList
import uvicorn

app = FastAPI()

@app.get("/scrape", response_model=CardList)
async def scrape_cards():
    data = []
    data = getCards()
    return data

@app.get("/cards", response_model=CardList)
async def get_all():
    data = []
    data = get_all_cards()
    return data

@app.get("/cards/sku/{sku_value}", response_model=Card)
async def get_card_by_sku(sku_value):
    if len(sku_value) != 6:
        raise  HTTPException(status_code=422, detail="sku is bad length")
    return get_card(sku_value)

@app.get("/cards/available/{available}", response_model=CardList)
async def get_card_by_available(available):
    print(available)
    if (available.lower() != "yes") and (available.lower() != "no"):
        raise  HTTPException(status_code=422, detail="please enter either Yes or No for availability") 
    return get_card_available(available.lower())

#uncomment to run debugger
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)