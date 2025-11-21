from pydantic import BaseModel
from uuid import UUID
from typing import Literal


class PaymentBase(BaseModel):
    price: int


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(BaseModel):
    payment_uid: UUID
    status: Literal["PAID", "CANCELED"]
    price: int

    class Config:
        from_attributes = True
