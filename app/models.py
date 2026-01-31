from typing import List, Optional, Dict
from pydantic import BaseModel

class IngredientOut(BaseModel):
    barcode: str
    ingredients: Optional[str]

class ParsedItem(BaseModel):
    raw: str
    name: Optional[str]
    amount: Optional[Dict]
    preparation: Optional[str]
    comment: Optional[str]
    confidence: Optional[float] = None
    error: Optional[str] = None

class ParsedResponse(BaseModel):
    barcode: str
    ingredients_raw: Optional[str]
    parsed: List[ParsedItem]
