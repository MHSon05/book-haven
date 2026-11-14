"""
Application DTOs: Admin & Warehouse Management
"""
from pydantic import BaseModel, Field


class RestockRequest(BaseModel):
    edition_id: str
    quantity: int = Field(gt=0)


class DispatchOrderRequest(BaseModel):
    carrier: str = "HANOI_DRONE"  # HANOI_DRONE hoặc GHN_EXPRESS
