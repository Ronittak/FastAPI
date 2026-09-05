from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship 

from database import Base

class Notebook(Base):
    __tablename__ = "notebooks"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    author = Column(String)

    entries = relationship("Entry",back_populates="notebook")

class Entry(Base):
    __tablename__="entries"
    id = Column(Integer,primary_key=True,index=True)
    heading = Column(String)
    mood = Column(String)
    word_count = Column(Integer)
    notebook_id = Column(Integer,ForeignKey("notebooks.id"))

    notebook = relationship("Notebook",back_populates="entries")