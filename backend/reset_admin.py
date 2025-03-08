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

def reset_admin_password():
    db = SessionLocal()
    try:
        # Get the admin user
        admin = db.query(models.Admin).filter(models.Admin.username == "lkamanboina").first()
        if admin:
            # Get new password from user
            new_password = input("Enter new password: ")
            
            # Hash the password using CryptContext
            hashed_password = pwd_context.hash(new_password)
            
            # Update the password
            admin.hashed_password = hashed_password
            db.commit()
            print("Admin password updated successfully!")
        else:
            print("Admin user not found!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password() 