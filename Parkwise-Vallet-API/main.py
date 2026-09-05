from typing import Optional,Literal
from fastapi import FastAPI,Response,Depends,HTTPException
from sqlalchemy.orm import Session

from database import engine,Base,get_db
from schemas import SlipCreate,SlipOut,LotWithSlips,LotCreate,LotOut,SlipTransfer
from models import Slip,Lot


Base.metadata.create_all(bind=engine)
app = FastAPI()



@app.post("/lots",response_model=LotOut,status_code=201)
def create_lot(lot:LotCreate,db:Session=Depends(get_db))->LotOut:
    new_lot = Lot(
        name=lot.name,
        zone=lot.zone 
    )
    db.add(new_lot)
    db.commit()
    db.refresh(new_lot)
    return new_lot

@app.post("/lots/{lot_id}/slips",response_model=SlipOut,status_code=201)
def add_slip(lot_id:int,slip:SlipCreate,db:Session=Depends(get_db))->SlipCreate:
    c1 = db.query(Lot).filter(Lot.id == lot_id).first()
    if not c1:
        raise HTTPException(status_code=404,detail="No lot with this id")

    

    new_slip = Slip(
        ticket_code = slip.ticket_code, 
        vehicle_class = slip.vehicle_class, 
        parked_minutes = slip.parked_minutes,
        lot_id = lot_id
    )

    db.add(new_slip)
    db.commit()
    db.refresh(new_slip)
    return new_slip

@app.get("/lots/{lot_id}",response_model=LotWithSlips,status_code=200)
def get_lot(lot_id:int,vehicle_class:Optional[str]=None,sort:Optional[Literal['ticket_code','parked_minutes']]=None,db:Session=Depends(get_db))->LotWithSlips:
    c1 = db.query(Lot).filter(Lot.id == lot_id).first()
    if not c1:
        raise HTTPException(status_code=404,detail="No such lot with this id")

    c2 = db.query(Slip).filter(Slip.lot_id == lot_id)
    if vehicle_class:
        c2 = c2.filter(Slip.vehicle_class == vehicle_class)
    if sort == 'ticket_code':
        c2 = c2.order_by(Slip.ticket_code)
    if sort == 'parked_minutes':
        c2 = c2.order_by(Slip.parked_minutes)

    all_slip = c2.all()
    return LotWithSlips(
        id=c1.id,
        name=c1.name,
        zone=c1.zone,
        slips=all_slip
    )

@app.post("/lots/{lot_id}/slips/transfer",response_model=LotWithSlips,status_code=200)
def transfer_slips(lot_id:int,transfer:SlipTransfer,db:Session=Depends(get_db))->LotWithSlips:
    source_lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not source_lot:
        raise HTTPException(status_code=404,detail="No lot with this id")

    target_lot = db.query(Lot).filter(Lot.id == transfer.target_lot_id).first()
    if not target_lot:
        raise HTTPException(status_code=404,detail="No such target lot")

    for sl in source_lot.slips:
        sl.lot_id = target_lot.id


    db.commit()
    db.refresh(target_lot)

    return target_lot
