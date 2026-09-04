from typing import List
from pydantic import BaseModel,Field,ConfigDict

class DepotCreate(BaseModel):
    name:str = Field(...)
    region:str = Field(...)

class DepotOut(BaseModel):
    id:int
    name:str
    region:str
    model_config = ConfigDict(from_attributes=True)



class VehicleCreate(BaseModel):
    plate_number:str = Field(...)
    vehicle_type:str = Field(...)
    mileage:int = Field(...,ge=0)

class VehicleOut(BaseModel):
    id:int
    plate_number:str
    vehicle_type:str
    mileage:int
    model_config = ConfigDict(from_attributes=True)

class DepotWithVehicles(BaseModel):
    id:int
    name:str
    region:str
    vehicles:List[VehicleOut]
    model_config = ConfigDict(from_attributes=True)