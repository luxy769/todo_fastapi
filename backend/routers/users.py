from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from database import get_db
from core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}