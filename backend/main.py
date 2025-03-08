from fastapi import FastAPI, Depends, HTTPException, Query, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import datetime, timedelta
import models, schemas
from database import engine, get_db, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, and_
from sqlalchemy.sql import func
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tech Events API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "http://localhost:3005", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password hashing functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_type: str = payload.get("user_type", "user")
        if username is None or user_type != "admin":
            raise credentials_exception
        token_data = schemas.TokenData(username=username, user_type=user_type)
    except JWTError:
        raise credentials_exception
    admin = db.query(models.Admin).filter(models.Admin.username == token_data.username).first()
    if admin is None:
        raise credentials_exception
    return admin

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        user_type: str = payload.get("user_type", "user")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, user_id=user_id, user_type=user_type)
    except JWTError:
        raise credentials_exception
        
    if token_data.user_type == "admin":
        user = db.query(models.Admin).filter(models.Admin.username == token_data.username).first()
    else:
        user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
        
    if user is None:
        raise credentials_exception
    return user

# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Check if it's an admin login
    admin = db.query(models.Admin).filter(models.Admin.username == form_data.username).first()
    if admin and verify_password(form_data.password, admin.hashed_password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": admin.username, "user_type": "admin"}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "admin",
            "username": admin.username
        }
    
    # Check if it's a user login
    user = db.query(models.User).filter(
        (models.User.username == form_data.username) | (models.User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_type": "user", "user_id": user.id}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "user",
        "user_id": user.id,
        "username": user.username
    }

@app.post("/admin/create", response_model=schemas.Admin)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(admin.password)
    db_admin = models.Admin(username=admin.username, hashed_password=hashed_password)
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

# User registration and profile management
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    db_user_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    db_user_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if hasattr(current_user, 'user_type') and current_user.user_type == "admin":
        raise HTTPException(status_code=400, detail="Admin accounts don't have user profiles")
    return current_user

@app.put("/users/me", response_model=schemas.User)
def update_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if hasattr(current_user, 'user_type') and current_user.user_type == "admin":
        raise HTTPException(status_code=400, detail="Admin accounts can't be updated through this endpoint")
    
    if user_update.email is not None:
        email_exists = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != current_user.id
        ).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    
    if user_update.interests is not None:
        current_user.interests = user_update.interests
    
    if user_update.profile_image is not None:
        current_user.profile_image = user_update.profile_image
    
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/users/me/save-event/{event_id}")
def save_event(
    event_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if event exists
    event = db.query(models.TechEvent).filter(models.TechEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if already saved
    if event_id in current_user.saved_events:
        # If already saved, remove it (toggle behavior)
        current_user.saved_events.remove(event_id)
    else:
        # If not saved, add it
        current_user.saved_events.append(event_id)
    
    db.commit()
    return {"success": True}

@app.post("/users/me/save-opportunity/{opportunity_id}")
def save_opportunity(
    opportunity_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if opportunity exists
    opportunity = db.query(models.ResearchOpportunity).filter(models.ResearchOpportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Check if already saved
    if opportunity_id in current_user.saved_opportunities:
        # If already saved, remove it (toggle behavior)
        current_user.saved_opportunities.remove(opportunity_id)
    else:
        # If not saved, add it
        current_user.saved_opportunities.append(opportunity_id)
    
    db.commit()
    return {"success": True}

@app.get("/users/me/saved-events", response_model=List[schemas.TechEvent])
def get_saved_events(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    events = db.query(models.TechEvent).filter(models.TechEvent.id.in_(current_user.saved_events)).all()
    return events

@app.get("/users/me/saved-opportunities", response_model=List[schemas.ResearchOpportunity])
def get_saved_opportunities(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    opportunities = db.query(models.ResearchOpportunity).filter(
        models.ResearchOpportunity.id.in_(current_user.saved_opportunities)
    ).all()
    return opportunities

@app.get("/events/", response_model=List[schemas.TechEvent])
def get_events(
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "start_date",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    query = db.query(models.TechEvent)
    
    # Apply sorting
    if sort_by == "start_date":
        query = query.order_by(models.TechEvent.start_date.asc())
    elif sort_by == "created_at":
        query = query.order_by(models.TechEvent.created_at.desc())
    elif sort_by == "likes":
        query = query.order_by(models.TechEvent.likes.desc())
    
    if sort_order == "desc":
        query = query.order_by(getattr(models.TechEvent, sort_by).desc())
    else:
        query = query.order_by(getattr(models.TechEvent, sort_by).asc())
    
    return query.offset(skip).limit(limit).all()

@app.get("/events/{event_id}", response_model=schemas.TechEvent)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.TechEvent).filter(models.TechEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.post("/events/", response_model=schemas.TechEvent)
def create_event(
    event: schemas.TechEventCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_event = models.TechEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events/search/")
def search_events(
    query: Optional[str] = None,
    location: Optional[str] = None,
    type: Optional[schemas.EventType] = None,
    virtual: Optional[bool] = None,
    start_date_after: Optional[datetime] = None,
    end_date_before: Optional[datetime] = None,
    tech_stack: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    events = db.query(models.TechEvent)
    
    filters = []
    
    if query:
        filters.append(
            or_(
                models.TechEvent.title.ilike(f"%{query}%"),
                models.TechEvent.description.ilike(f"%{query}%"),
                models.TechEvent.organization.ilike(f"%{query}%")
            )
        )
    
    if location:
        filters.append(models.TechEvent.location.ilike(f"%{location}%"))
    
    if type:
        filters.append(models.TechEvent.type == type)
    
    if virtual is not None:
        filters.append(models.TechEvent.virtual == virtual)
    
    if start_date_after:
        filters.append(models.TechEvent.start_date >= start_date_after)
    
    if end_date_before:
        filters.append(models.TechEvent.end_date <= end_date_before)
    
    if tech_stack:
        for tech in tech_stack:
            filters.append(models.TechEvent.tech_stack.contains([tech]))
    
    if tags:
        for tag in tags:
            filters.append(models.TechEvent.tags.contains([tag]))
    
    if filters:
        events = events.filter(and_(*filters))
    
    return events.order_by(models.TechEvent.start_date.asc()).all()

@app.get("/events/stats/")
def get_stats(db: Session = Depends(get_db)):
    total_events = db.query(models.TechEvent).count()
    total_attendees = db.query(func.sum(models.TechEvent.attendees)).scalar() or 0
    total_likes = db.query(func.sum(models.TechEvent.likes)).scalar() or 0
    
    types = db.query(models.TechEvent.type, func.count()).group_by(models.TechEvent.type).all()
    virtual_vs_physical = db.query(models.TechEvent.virtual, func.count()).group_by(models.TechEvent.virtual).all()
    
    upcoming_events = db.query(models.TechEvent).filter(models.TechEvent.start_date >= datetime.now()).count()
    
    return {
        "total_events": total_events,
        "total_attendees": total_attendees,
        "total_likes": total_likes,
        "types": dict(types),
        "virtual_vs_physical": dict(virtual_vs_physical),
        "upcoming_events": upcoming_events
    }

@app.put("/events/{event_id}", response_model=schemas.TechEvent)
def update_event(
    event_id: int,
    event: schemas.TechEventCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_event = db.query(models.TechEvent).filter(models.TechEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event.dict().items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@app.delete("/events/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_event = db.query(models.TechEvent).filter(models.TechEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return {"message": "Event deleted"}

@app.post("/events/{event_id}/like")
def like_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.TechEvent).filter(models.TechEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.likes += 1
    db.commit()
    return {"message": "Event liked successfully", "likes": event.likes}

@app.post("/events/{event_id}/register")
def register_for_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.TechEvent).filter(models.TechEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.attendees += 1
    db.commit()
    return {"message": "Successfully registered for event", "attendees": event.attendees}

@app.get("/opportunities/", response_model=List[schemas.ResearchOpportunity])
def get_opportunities(
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "deadline",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    query = db.query(models.ResearchOpportunity)
    
    # Apply sorting
    if sort_by == "deadline":
        query = query.order_by(models.ResearchOpportunity.deadline.asc())
    elif sort_by == "created_at":
        query = query.order_by(models.ResearchOpportunity.created_at.desc())
    elif sort_by == "likes":
        query = query.order_by(models.ResearchOpportunity.likes.desc())
    
    if sort_order == "desc":
        query = query.order_by(getattr(models.ResearchOpportunity, sort_by).desc())
    else:
        query = query.order_by(getattr(models.ResearchOpportunity, sort_by).asc())
    
    return query.offset(skip).limit(limit).all()

@app.get("/opportunities/{opportunity_id}", response_model=schemas.ResearchOpportunity)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    opportunity = db.query(models.ResearchOpportunity).filter(models.ResearchOpportunity.id == opportunity_id).first()
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@app.post("/opportunities/", response_model=schemas.ResearchOpportunity)
def create_opportunity(
    opportunity: schemas.ResearchOpportunityCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_opportunity = models.ResearchOpportunity(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

@app.get("/opportunities/search/")
def search_opportunities(
    query: Optional[str] = None,
    location: Optional[str] = None,
    type: Optional[schemas.OpportunityType] = None,
    virtual: Optional[bool] = None,
    deadline_after: Optional[datetime] = None,
    fields: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    opportunities = db.query(models.ResearchOpportunity)
    
    filters = []
    
    if query:
        filters.append(
            or_(
                models.ResearchOpportunity.title.ilike(f"%{query}%"),
                models.ResearchOpportunity.description.ilike(f"%{query}%"),
                models.ResearchOpportunity.organization.ilike(f"%{query}%")
            )
        )
    
    if location:
        filters.append(models.ResearchOpportunity.location.ilike(f"%{location}%"))
    
    if type:
        filters.append(models.ResearchOpportunity.type == type)
    
    if virtual is not None:
        filters.append(models.ResearchOpportunity.virtual == virtual)
    
    if deadline_after:
        filters.append(models.ResearchOpportunity.deadline >= deadline_after)
    
    if fields:
        for field in fields:
            filters.append(models.ResearchOpportunity.fields.contains([field]))
    
    if tags:
        for tag in tags:
            filters.append(models.ResearchOpportunity.tags.contains([tag]))
    
    if filters:
        opportunities = opportunities.filter(and_(*filters))
    
    return opportunities.order_by(models.ResearchOpportunity.deadline.asc()).all()

@app.get("/opportunities/stats/")
def get_opportunity_stats(db: Session = Depends(get_db)):
    total_opportunities = db.query(models.ResearchOpportunity).count()
    total_applications = db.query(func.sum(models.ResearchOpportunity.applications)).scalar() or 0
    total_likes = db.query(func.sum(models.ResearchOpportunity.likes)).scalar() or 0
    
    types = db.query(models.ResearchOpportunity.type, func.count()).group_by(models.ResearchOpportunity.type).all()
    virtual_vs_physical = db.query(models.ResearchOpportunity.virtual, func.count()).group_by(models.ResearchOpportunity.virtual).all()
    
    upcoming_opportunities = db.query(models.ResearchOpportunity).filter(models.ResearchOpportunity.deadline >= datetime.now()).count()
    
    return {
        "total_opportunities": total_opportunities,
        "total_applications": total_applications,
        "total_likes": total_likes,
        "types": dict(types),
        "virtual_vs_physical": dict(virtual_vs_physical),
        "upcoming_opportunities": upcoming_opportunities
    }

@app.put("/opportunities/{opportunity_id}", response_model=schemas.ResearchOpportunity)
def update_opportunity(
    opportunity_id: int,
    opportunity: schemas.ResearchOpportunityCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_opportunity = db.query(models.ResearchOpportunity).filter(models.ResearchOpportunity.id == opportunity_id).first()
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    for key, value in opportunity.dict().items():
        setattr(db_opportunity, key, value)
    
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

@app.delete("/opportunities/{opportunity_id}")
def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_opportunity = db.query(models.ResearchOpportunity).filter(models.ResearchOpportunity.id == opportunity_id).first()
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    db.delete(db_opportunity)
    db.commit()
    return {"message": "Opportunity deleted"}

@app.post("/opportunities/{opportunity_id}/like")
def like_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    db_opportunity = db.query(models.ResearchOpportunity).filter(models.ResearchOpportunity.id == opportunity_id).first()
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    db_opportunity.likes += 1
    db.commit()
    return {"message": "Like recorded"}

@app.post("/opportunities/{opportunity_id}/apply")
def apply_for_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    db_opportunity = db.query(models.ResearchOpportunity).filter(models.ResearchOpportunity.id == opportunity_id).first()
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    db_opportunity.applications += 1
    db.commit()
    return {"message": "Application recorded"}
