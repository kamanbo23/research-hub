from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_admin():
    db = SessionLocal()
    try:
        # Delete the admin user
        db.query(models.Admin).filter(models.Admin.username == "lkamanboina").delete()
        db.commit()
        print("Admin user deleted successfully!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_admin() 