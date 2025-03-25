from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Task
from database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/")
def create_task(title: str, description: str, db: Session = Depends(get_db)):
    task = Task(title=title, description=description)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/")
def read_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()
