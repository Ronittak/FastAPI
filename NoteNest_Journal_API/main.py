from typing import Optional,Literal
from fastapi import FastAPI,Response,HTTPException,Depends
from sqlalchemy.orm import Session

from database import engine,Base,get_db
from schemas import NotebookCreate,NotebookOut,NotebookWithEntries,EntryCreate,EntryOut
from models import Notebook,Entry

Base.metadata.create_all(bind = engine)
app = FastAPI()

@app.post("/notebooks",response_model=NotebookOut,status_code=201)
def create_notebook(notebook:NotebookCreate,db:Session=Depends(get_db))->NotebookOut:
    new_notebook = Notebook(
        title = notebook.title,
        author = notebook.author
    )
    db.add(new_notebook)
    db.commit()
    db.refresh(new_notebook)
    return new_notebook

@app.post("/notebooks/{notebook_id}/entries",response_model=EntryOut,status_code=201)
def add_entry(notebook_id:int,entry:EntryCreate,db:Session=Depends(get_db))->EntryOut:
    c1 = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not c1:
        raise HTTPException(status_code=404,detail="No such notebook with this id")
    new_entry = Entry(
        heading = entry.heading,
        mood = entry.mood,
        word_count = entry.word_count,
        notebook_id = notebook_id
        
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@app.get("/notebooks/{notebook_id}",response_model=NotebookWithEntries,status_code=200)
def get_notebook(notebook_id:int,mood:Optional[str]=None,sort:Optional[Literal['heading','word_count']]=None,db:Session=Depends(get_db))->NotebookWithEntries:
    c1 = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not c1:
        raise HTTPException(status_code=404,detail="No notebook of such id")

    c2 = db.query(Entry).filter(Entry.notebook_id == notebook_id)
    if mood:
        c2 = c2.filter(Entry.mood == mood)
    if sort == 'heading':
        c2 = c2.order_by(Entry.heading)
    if sort == 'word_count':
        c2 = c2.order_by(Entry.word_count)

    all_entries = c2.all()
    return NotebookWithEntries(
        id = c1.id,
        title=c1.title,
        author=c1.author,
        entries=all_entries
    )

@app.delete("/notebooks/{notebook_id}/entries",status_code=204)
def clear_entries(notebook_id:int,db:Session=Depends(get_db))->None:
    c1 = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not c1:
        raise HTTPException(status_code=404,detail="No such notebook with this id")

    db.query(Entry).filter(Entry.notebook_id == notebook_id).delete(synchronize_session=False)    
    db.commit()
    return Response(status_code=204)
