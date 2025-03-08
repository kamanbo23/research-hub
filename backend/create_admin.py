from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    db = SessionLocal()
    try:
        # Create tables if they don't exist
        models.Base.metadata.create_all(bind=engine)
        
        # Get admin credentials
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        
        # Check if admin already exists
        existing_admin = db.query(models.Admin).filter(models.Admin.username == username).first()
        if existing_admin:
            print(f"Admin user '{username}' already exists")
            return
        
        # Hash the password using CryptContext
        hashed_password = pwd_context.hash(password)
        
        # Create new admin
        admin = models.Admin(
            username=username,
            hashed_password=hashed_password
        )
        
        db.add(admin)
        db.commit()
        print(f"Admin user '{username}' created successfully!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin() 