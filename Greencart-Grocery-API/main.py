from typing import Optional
from fastapi import FastAPI,Response,Query,Depends,HTTPException
from sqlalchemy.orm import Session

from database import Base,get_db,engine
from schemas import StoreCreate,StoreOut,StoreWithItems,ItemCreate,ItemOut
from models import Store,Item

Base.metadata.create_all(bind = engine)
app = FastAPI()

@app.post("/stores",response_model=StoreOut,status_code=201)
def create_store(store:StoreCreate,db:Session=Depends(get_db))->StoreOut:
    new_store = Store(
        name = store.name,
        city = store.city
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store



@app.post("/stores/{store_id}/items",response_model=ItemOut,status_code=201)
def add_item(store_id:int,item:ItemCreate,db:Session=Depends(get_db))->ItemOut:
    c1 = db.query(Store).filter(Store.id == store_id).first()
    if not c1:
        raise HTTPException(status_code=404,detail="No such store id")

    new_item = Item(
        name = item.name,
        category = item.category,
        stock_qty = item.stock_qty,
        store_id = store_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

    

@app.get("/stores/{store_id}",response_model=StoreWithItems,status_code=200)
def get_store(store_id:int,category:Optional[str]=None,sort:Optional[str]=None,db:Session=Depends(get_db))->StoreWithItems:
    c1 = db.query(Store).filter(Store.id == store_id).first()
    if not c1:
        raise HTTPException(
            status_code = 404,
            detail="No store with such id"
        )
    c2 = db.query(Item).filter(Item.store_id == store_id)
    if category:
        c2 = c2.filter(Item.category == category)
    
    if sort:
        if sort == "name":
            c2 = c2.order_by(Item.name)
        if sort == "stock_qty":
            c2 = c2.order_by(Item.stock_qty)
        else:
            raise HTTPException(
                status_code=422,
                detail="Invalid Sort"
            )

    all_items = c2.all()
    return StoreWithItems(
        id = c1.id,
        name = c1.name,
        city = c1.city,
        items = all_items 
    )

@app.delete("/stores/{store_id}/items/{item_id}",status_code=204)
def delete_item(store_id:int,item_id:int,db:Session=Depends(get_db))->None:
    c1 = db.query(Store).filter(Store.id == store_id).first()
    if not c1:
        raise HTTPException(
            status_code = 404,
            detail="No store with such id"
        )
    c2 = db.query(Item).filter(Store.id == store_id,Item.id ==  item_id).first()
    db.delete(c2)
    db.commit()
    return Response(status_code=204)
    