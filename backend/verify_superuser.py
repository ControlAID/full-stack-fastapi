from sqlmodel import Session, create_engine, select
from app.models import User
from app.core import security
import os
import sys

# Internal Docker connection details (defaults)
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "4PYAm8qwN27pqSUUWl29wltsBbDNjb5DfHPEK2Evhqg")

DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

def verify(email, password):
    engine = create_engine(DATABASE_URL)
    try:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                print(f"Error: User {email} not found")
                return False
            
            is_valid = security.verify_password(password, user.hashed_password)
            if is_valid:
                print(f"Success: Password for {email} is correct")
                print(f"User details: Superuser={user.is_superuser}, Active={user.is_active}")
                return True
            else:
                print(f"Error: Incorrect password for {email}")
                return False
    except Exception as e:
        print(f"Database error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Defaults from .env if not provided
        email = os.getenv("FIRST_SUPERUSER", "admin@example.com")
        password = os.getenv("FIRST_SUPERUSER_PASSWORD", "KSZOOaT6shoLvy-tuKe8PZkvj_XSXkHp_NLECFpVy7Y")
    else:
        email = sys.argv[1]
        password = sys.argv[2]
    
    print(f"Verifying credentials for {email}...")
    verify(email, password)
