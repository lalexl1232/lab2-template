from pydantic import BaseModel
from uuid import UUID
from typing import Literal, Optional


class CarResponse(BaseModel):
    car_uid: UUID
    brand: str
    model: str
    registration_number: str
    power: Optional[int] = None
    price: int
    type: str
    available: bool


class PaginationResponse(BaseModel):
    page: int
    page_size: int
    total_elements: int
    items: list[CarResponse]


class CarInfo(BaseModel):
    car_uid: UUID
    brand: str
    model: str
    registration_number: str


class PaymentInfo(BaseModel):
    payment_uid: UUID
    status: Literal["PAID", "CANCELED"]
    price: int


class RentalResponse(BaseModel):
    rental_uid: UUID
    status: Literal["IN_PROGRESS", "FINISHED", "CANCELED"]
    date_from: str
    date_to: str
    car: CarInfo
    payment: PaymentInfo


class CreateRentalRequest(BaseModel):
    car_uid: UUID
    date_from: str
    date_to: str


class CreateRentalResponse(BaseModel):
    rental_uid: UUID
    status: Literal["IN_PROGRESS", "FINISHED", "CANCELED"]
    car_uid: UUID
    date_from: str
    date_to: str
    payment: PaymentInfo


class ErrorResponse(BaseModel):
    message: str
