from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from .. import models, schemas


router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/create_post", response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    author = db.query(models.User).filter(models.User.id == post.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

from backend import models, schemas
