from database import engine
import models

print("Creating database tables...")
models.Base.metadata.create_all(bind=engine)
print("Database tables created successfully!") 