from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Literal


class RentalBase(BaseModel):
    username: str
    payment_uid: UUID
    car_uid: UUID
    date_from: str
    date_to: str


class RentalCreate(RentalBase):
    pass


class RentalResponse(BaseModel):
    rental_uid: UUID
    username: str
    payment_uid: UUID
    car_uid: UUID
    date_from: str
    date_to: str
    status: Literal["IN_PROGRESS", "FINISHED", "CANCELED"]

    class Config:
        from_attributes = True
