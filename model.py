from pydantic import BaseModel
from typing import List


class Card(BaseModel):
    sku_value: str
    card_name: str
    available: str


class CardList(BaseModel):
    cards: List[Card]

    class Config:
        orm_mode = True
