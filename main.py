from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Car(BaseModel):
    car_id: str

class CarPark:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.available_spaces = capacity
        self.occupied_spaces = []
        self.queue = []

    def enter(self, car: Car):
        if self.available_spaces == 0:
            self.queue.append(car.car_id)
            raise HTTPException(status_code=409, detail="Car park is full, joined queue")
        self.available_spaces -= 1
        self.occupied_spaces.append(car.car_id)
        return True

    def exit(self, car: Car):
        if car.car_id not in self.occupied_spaces:
            raise HTTPException(status_code=404, detail="Car not found in car park")
        self.available_spaces += 1
        self.occupied_spaces.remove(car.car_id)
        if self.queue:
            next_car = self.queue.pop(0)
            self.enter(Car(car_id=next_car))

    def get_status(self):
        return {
            "total_cars": len(self.occupied_spaces),
            "available_spaces": self.available_spaces,
        }

    def get_queue(self):
        return self.queue

car_park = CarPark(capacity=3)

@app.post("/api/cars/enter")
async def enter_car(car: Car):
    try:
        car_park.enter(car)
        return {"success": True, "message": "Car entered successfully"}
    except HTTPException as e:
        return {"success": False, "message": e.detail}

@app.post("/api/cars/exit")
async def exit_car(car: Car):
    try:
        car_park.exit(car)
        return {"success": True, "message": "Car exited successfully"}
    except HTTPException as e:
        return {"success": False, "message": e.detail}

@app.get("/api/cars/count")
async def get_car_count():
    return car_park.get_status()

@app.get("/api/cars/queue")
async def get_car_queue():
    return {"queue": car_park.get_queue()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)