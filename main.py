from typing import Optional
from fastapi import FastAPI,HTTPException,Query,Response,Depends
from sqlalchemy.orm import Session
import uvicorn

from database import engine,Base,get_db
from models import Depot,Vehicle
from schemas import DepotCreate,DepotOut,DepotWithVehicles,VehicleOut,VehicleCreate

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/depots",response_model = DepotOut,status_code=201)
def create_depot(depot:DepotCreate,db:Session = Depends(get_db)) -> DepotOut:
    new_depot = Depot(
        name = depot.name,
        region = depot.region,
    )
    db.add(new_depot)
    db.commit()
    db.refresh(new_depot)
    return new_depot

@app.post("/depots/{depot_id}/vehicles",response_model=VehicleOut,status_code=201)
def add_vehicle(depot_id:int,vehicle:VehicleCreate,db:Session = Depends(get_db))->VehicleOut:
    c = db.query(Depot).filter(Depot.id == depot_id).first()

    if not c:
        raise HTTPException(status_code=404,detail="No depot with such id")

    new_vehicle = Vehicle(
        plate_number = vehicle.plate_number,
        vehicle_type = vehicle.vehicle_type,
        mileage = vehicle.mileage,
        depot_id = depot_id
    )

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle

@app.get("/depots/{depot_id}",response_model=DepotWithVehicles,status_code=200)
def get_depot(depot_id:int,vehicle_type:Optional[str]=None,sort:Optional[str]=None,db:Session=Depends(get_db))->DepotWithVehicles:
    c1 = db.query(Depot).filter(Depot.id == depot_id).first()   
    if c1 is None:
        raise HTTPException(status_code=404,detail="No such depot")
    c2 = db.query(Vehicle).filter(Vehicle.depot_id == depot_id)

    if vehicle_type:
        c2 = c2.filter(Vehicle.vehicle_type == vehicle_type)

    if sort:
        if sort == 'plate_number':
            c2 = c2.order_by(Vehicle.plate_number)
        if sort == 'mileage':
            c2 = c2.order_by(Vehicle.mileage)

    all_vehicles = c2.all()

    return DepotWithVehicles(
        id = c1.id,
        name = c1.name,
        region = c1.region,
        vehicles=all_vehicles
    )

@app.put("/depots/{depot_id}/vehicles/{vehicle_id}",response_model=VehicleOut,status_code=200)
def update_vehicle(depot_id:int,vehicle_id:int,vehicle:VehicleCreate,db:Session=Depends(get_db))->VehicleOut:
    c1 = db.query(Depot).filter(Depot.id == depot_id).first()
    if c1 is None:
        raise HTTPException(status_code=404,detail="No such Depot")
    
    c2 = db.query(Vehicle).filter(Vehicle.depot_id == depot_id,Vehicle.id == vehicle_id).first()

    if c2 is None:
        raise HTTPException(status_code=404,detail="No such Vehicle")

    c2.plate_number = vehicle.plate_number
    c2.vehicle_type = vehicle.vehicle_type
    c2.mileage = vehicle.mileage

    db.commit()
    db.refresh(c2)
    return c2



    