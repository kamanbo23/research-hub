from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from passlib.context import CryptContext
from .. import models, schemas


router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) |
        (models.User.username == user.username)
    ).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(**user.dict(exclude={"password"}), password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

from backend import models, schemas
