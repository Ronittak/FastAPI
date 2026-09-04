from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    city = Column(String)

    items = relationship("Item",back_populates="stores",cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    category = Column(String)
    stock_qty = Column(String)
    store_id = Column(Integer,ForeignKey("stores.id"))

    stores = relationship("Store",back_populates="items")