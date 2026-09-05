from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Lot(Base):
    __tablename__="lots"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    zone = Column(String)

    slips = relationship("Slip",back_populates="lot",cascade="all, delete-orphan")

class Slip(Base):
    __tablename__ = "slips"
    id = Column(Integer,primary_key=True,index=True)
    ticket_code = Column(String) 
    vehicle_class = Column(String) 
    parked_minutes = Column(Integer)

    lot_id = Column(Integer,ForeignKey("lots.id"))

    lot = relationship("Lot",back_populates="slips")