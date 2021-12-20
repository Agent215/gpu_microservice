from typing import Optional
from pydantic import BaseModel ,json
from fastapi import FastAPI, HTTPException
from scrape_cards import getCards
from init_db import get_all_cards, get_card
from typing import List
import uvicorn



app = FastAPI()

class Card(BaseModel):
    sku_value: str
    card_name: str
    available: str


class CardList(BaseModel):
    cards :List[Card]
    class Config:
        orm_mode = True


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

@app.get("/cards/{sku_value}", response_model=Card)
async def read_item(sku_value):
    if len(sku_value) != 6:
        raise  HTTPException(status_code=422, detail="sku is bad length")
    return get_card(sku_value)

@app.get("/cards/{available}", response_model=CardList)
async def read_item(available):
    return get_card_available(available)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)