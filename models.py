from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Depot(Base):
    __tablename__ = "depots"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    region = Column(String)
    vehicles = relationship("Vehicle",back_populates = "depot",cascade="all, delete-orphan")

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer,primary_key=True,index=True)

    plate_number = Column(String)
    vehicle_type = Column(String)
    mileage = Column(Integer)
    depot_id = Column(Integer,ForeignKey("depots.id"))

    depot = relationship("Depot",back_populates="vehicles")
