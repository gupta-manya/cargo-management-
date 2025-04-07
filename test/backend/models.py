# models.py
from pydantic import BaseModel
from typing import Optional
from datetime import date
class Item(BaseModel):
    item_id: str
    name: str
    width_cm: float
    depth_cm: float
    height_cm: float
    mass_kg: float
    priority: int
    expiry_date: Optional[date]
    usage_limit: int
    preferred_zone: str

class Container(BaseModel):
    zone: str
    container_id: str
    width_cm: float
    depth_cm: float
    height_cm: float
    

class RetrievalLog(BaseModel):
    item_id: str
    astronaut: str
    retrieved_at: date
    from_container: str