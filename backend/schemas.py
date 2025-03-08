from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    CONFERENCE = "Conference"
    HACKATHON = "Hackathon"
    WORKSHOP = "Workshop"
    MEETUP = "Meetup"
    WEBINAR = "Webinar"
    TECH_TALK = "Tech Talk"

class OpportunityType(str, Enum):
    RESEARCH = "Research"
    INTERNSHIP = "Internship"
    FELLOWSHIP = "Fellowship"
    GRANT = "Grant"
    PROJECT = "Project"

class AdminBase(BaseModel):
    username: str

class AdminCreate(AdminBase):
    password: str

class Admin(AdminBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str
    full_name: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[List[str]] = None
    profile_image: Optional[str] = None

class User(UserBase):
    id: int
    full_name: str
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool
    interests: List[str] = []
    saved_events: List[int] = []
    saved_opportunities: List[int] = []
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str = "user"  # "admin" or "user"
    user_id: Optional[int] = None
    username: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    user_type: Optional[str] = None

class TechEventBase(BaseModel):
    title: str
    organization: str
    description: str
    venue: str
    registration_link: str
    start_date: datetime
    end_date: datetime
    location: str
    type: EventType
    price: Optional[str] = None
    tech_stack: List[str] = []  # e.g., ["Python", "React", "AWS"]
    speakers: List[str] = []
    virtual: bool = False
    tags: List[str] = []

class TechEventCreate(TechEventBase):
    pass

class TechEvent(TechEventBase):
    id: int
    created_at: datetime
    updated_at: datetime
    attendees: int = 0
    likes: int = 0

    class Config:
        from_attributes = True

class ResearchOpportunityBase(BaseModel):
    title: str
    organization: str
    description: str
    type: OpportunityType
    location: str
    deadline: datetime
    duration: Optional[str] = None
    compensation: Optional[str] = None
    requirements: List[str] = []
    fields: List[str] = []  # e.g., ["Machine Learning", "Computer Vision"]
    contact_email: str
    virtual: bool = False
    tags: List[str] = []

class ResearchOpportunityCreate(ResearchOpportunityBase):
    pass

class ResearchOpportunity(ResearchOpportunityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    applications: int = 0
    likes: int = 0

    class Config:
        from_attributes = True