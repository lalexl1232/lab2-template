from pydantic import BaseModel
from uuid import UUID
from typing import Literal, Optional


class CarBase(BaseModel):
    brand: str
    model: str
    registration_number: str
    power: Optional[int] = None
    price: int
    type: Literal["SEDAN", "SUV", "MINIVAN", "ROADSTER"]
    availability: bool = True


class CarCreate(CarBase):
    pass


class CarResponse(BaseModel):
    car_uid: UUID
    brand: str
    model: str
    registration_number: str
    power: Optional[int] = None
    price: int
    type: str
    available: bool

    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    page: int
    page_size: int
    total_elements: int
    items: list[CarResponse]
