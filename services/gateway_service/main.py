from fastapi import FastAPI, Header, HTTPException, Query
from typing import Optional, List
import httpx
import uvicorn
from datetime import datetime
import os

from schemas import (
    PaginationResponse, RentalResponse, CreateRentalRequest,
    CreateRentalResponse, CarInfo, PaymentInfo, ErrorResponse
)

app = FastAPI(title="Gateway Service")

CARS_SERVICE_URL = os.getenv("CARS_SERVICE_URL", "http://cars:8070")
RENTAL_SERVICE_URL = os.getenv("RENTAL_SERVICE_URL", "http://rental:8060")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment:8050")


@app.get("/manage/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/cars", response_model=PaginationResponse)
async def get_cars(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    show_all: bool = Query(False, alias="showAll")
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CARS_SERVICE_URL}/api/v1/cars",
            params={"page": page, "size": size, "show_all": show_all}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Cars service error")
        return response.json()


@app.post("/api/v1/rental", response_model=CreateRentalResponse)
async def create_rental(
    rental_request: CreateRentalRequest,
    x_user_name: str = Header(..., alias="X-User-Name")
):
    async with httpx.AsyncClient() as client:
        # Get car details
        car_response = await client.get(
            f"{CARS_SERVICE_URL}/api/v1/cars/{rental_request.car_uid}"
        )
        if car_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Car not found")

        car_data = car_response.json()

        # Calculate rental price
        date_from = datetime.fromisoformat(rental_request.date_from)
        date_to = datetime.fromisoformat(rental_request.date_to)
        days = abs((date_to - date_from).days)
        total_price = days * car_data["price"]

        # Create payment
        payment_response = await client.post(
            f"{PAYMENT_SERVICE_URL}/api/v1/payment",
            json={"price": total_price}
        )
        if payment_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Payment service error")

        payment_data = payment_response.json()

        # Reserve car
        reserve_response = await client.patch(
            f"{CARS_SERVICE_URL}/api/v1/cars/{rental_request.car_uid}/availability",
            params={"available": False}
        )
        if reserve_response.status_code != 200:
            # Rollback payment
            await client.delete(f"{PAYMENT_SERVICE_URL}/api/v1/payment/{payment_data['payment_uid']}")
            raise HTTPException(status_code=500, detail="Failed to reserve car")

        # Create rental
        rental_response = await client.post(
            f"{RENTAL_SERVICE_URL}/api/v1/rental",
            json={
                "username": x_user_name,
                "payment_uid": payment_data["payment_uid"],
                "car_uid": str(rental_request.car_uid),
                "date_from": rental_request.date_from,
                "date_to": rental_request.date_to
            }
        )
        if rental_response.status_code != 200:
            # Rollback car availability and payment
            await client.patch(
                f"{CARS_SERVICE_URL}/api/v1/cars/{rental_request.car_uid}/availability",
                params={"available": True}
            )
            await client.delete(f"{PAYMENT_SERVICE_URL}/api/v1/payment/{payment_data['payment_uid']}")
            raise HTTPException(status_code=500, detail="Rental service error")

        rental_data = rental_response.json()

        return CreateRentalResponse(
            rental_uid=rental_data["rental_uid"],
            status=rental_data["status"],
            car_uid=rental_request.car_uid,
            date_from=rental_request.date_from,
            date_to=rental_request.date_to,
            payment=PaymentInfo(
                payment_uid=payment_data["payment_uid"],
                status=payment_data["status"],
                price=payment_data["price"]
            )
        )


@app.get("/api/v1/rental", response_model=List[RentalResponse])
async def get_user_rentals(x_user_name: str = Header(..., alias="X-User-Name")):
    async with httpx.AsyncClient() as client:
        # Get all rentals for user
        rentals_response = await client.get(
            f"{RENTAL_SERVICE_URL}/api/v1/rental",
            params={"username": x_user_name}
        )
        if rentals_response.status_code != 200:
            raise HTTPException(status_code=rentals_response.status_code, detail="Rental service error")

        rentals = rentals_response.json()
        result = []

        for rental in rentals:
            # Get car info
            car_response = await client.get(
                f"{CARS_SERVICE_URL}/api/v1/cars/{rental['car_uid']}"
            )
            car_data = car_response.json() if car_response.status_code == 200 else {}

            # Get payment info
            payment_response = await client.get(
                f"{PAYMENT_SERVICE_URL}/api/v1/payment/{rental['payment_uid']}"
            )
            payment_data = payment_response.json() if payment_response.status_code == 200 else {}

            result.append(RentalResponse(
                rental_uid=rental["rental_uid"],
                status=rental["status"],
                date_from=rental["date_from"],
                date_to=rental["date_to"],
                car=CarInfo(
                    car_uid=car_data.get("car_uid", rental["car_uid"]),
                    brand=car_data.get("brand", ""),
                    model=car_data.get("model", ""),
                    registration_number=car_data.get("registration_number", "")
                ),
                payment=PaymentInfo(
                    payment_uid=payment_data.get("payment_uid", rental["payment_uid"]),
                    status=payment_data.get("status", "PAID"),
                    price=payment_data.get("price", 0)
                )
            ))

        return result


@app.get("/api/v1/rental/{rental_uid}", response_model=RentalResponse)
async def get_rental(
    rental_uid: str,
    x_user_name: str = Header(..., alias="X-User-Name")
):
    async with httpx.AsyncClient() as client:
        # Get rental
        rental_response = await client.get(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}",
            params={"username": x_user_name}
        )
        if rental_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Rental not found")
        if rental_response.status_code != 200:
            raise HTTPException(status_code=rental_response.status_code, detail="Rental service error")

        rental = rental_response.json()

        # Get car info
        car_response = await client.get(
            f"{CARS_SERVICE_URL}/api/v1/cars/{rental['car_uid']}"
        )
        car_data = car_response.json() if car_response.status_code == 200 else {}

        # Get payment info
        payment_response = await client.get(
            f"{PAYMENT_SERVICE_URL}/api/v1/payment/{rental['payment_uid']}"
        )
        payment_data = payment_response.json() if payment_response.status_code == 200 else {}

        return RentalResponse(
            rental_uid=rental["rental_uid"],
            status=rental["status"],
            date_from=rental["date_from"],
            date_to=rental["date_to"],
            car=CarInfo(
                car_uid=car_data.get("car_uid", rental["car_uid"]),
                brand=car_data.get("brand", ""),
                model=car_data.get("model", ""),
                registration_number=car_data.get("registration_number", "")
            ),
            payment=PaymentInfo(
                payment_uid=payment_data.get("payment_uid", rental["payment_uid"]),
                status=payment_data.get("status", "PAID"),
                price=payment_data.get("price", 0)
            )
        )


@app.delete("/api/v1/rental/{rental_uid}", status_code=204)
async def cancel_rental(
    rental_uid: str,
    x_user_name: str = Header(..., alias="X-User-Name")
):
    async with httpx.AsyncClient() as client:
        # Get rental to get car_uid and payment_uid
        rental_response = await client.get(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}",
            params={"username": x_user_name}
        )
        if rental_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Rental not found")
        if rental_response.status_code != 200:
            raise HTTPException(status_code=rental_response.status_code, detail="Rental service error")

        rental = rental_response.json()

        # Cancel rental
        cancel_response = await client.delete(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}",
            params={"username": x_user_name}
        )
        if cancel_response.status_code != 204:
            raise HTTPException(status_code=cancel_response.status_code, detail="Failed to cancel rental")

        # Release car
        await client.patch(
            f"{CARS_SERVICE_URL}/api/v1/cars/{rental['car_uid']}/availability",
            params={"available": True}
        )

        # Cancel payment
        await client.delete(f"{PAYMENT_SERVICE_URL}/api/v1/payment/{rental['payment_uid']}")

        return None


@app.post("/api/v1/rental/{rental_uid}/finish", status_code=204)
async def finish_rental(
    rental_uid: str,
    x_user_name: str = Header(..., alias="X-User-Name")
):
    async with httpx.AsyncClient() as client:
        # Get rental to get car_uid
        rental_response = await client.get(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}",
            params={"username": x_user_name}
        )
        if rental_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Rental not found")
        if rental_response.status_code != 200:
            raise HTTPException(status_code=rental_response.status_code, detail="Rental service error")

        rental = rental_response.json()

        # Finish rental
        finish_response = await client.post(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}/finish",
            params={"username": x_user_name}
        )
        if finish_response.status_code != 204:
            raise HTTPException(status_code=finish_response.status_code, detail="Failed to finish rental")

        # Release car
        await client.patch(
            f"{CARS_SERVICE_URL}/api/v1/cars/{rental['car_uid']}/availability",
            params={"available": True}
        )

        return None


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
