import logging
import uuid
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.core.db import engine, init_db
from app.core.security import get_password_hash
from app.models import (
    Organization, User, License, LicenseTier,
    OrganizationCreate, UserCreate
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data() -> None:
    with Session(engine) as session:
        # 1. Create Organization
        org_name = "Test Security Corp"
        statement = select(Organization).where(Organization.name == org_name)
        org = session.exec(statement).first()
        
        if not org:
            org = Organization(
                name=org_name,
                type="commercial",
                address="123 Database St.",
                contact_email="admin@testcorp.com",
                is_active=True
            )
            session.add(org)
            session.commit()
            session.refresh(org)
            logger.info(f"Created Organization: {org.name} (ID: {org.id})")
        else:
            logger.info(f"Organization already exists: {org.name}")

        # 2. Create User
        email = "admin@testcorp.com"
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        password = "password123"
        hashed_password = get_password_hash(password)
        
        if not user:
            user = User(
                email=email,
                hashed_password=hashed_password,
                full_name="Admin Test",
                organization_id=org.id,
                is_superuser=False,
                is_active=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Created User: {user.email}")
        else:
            logger.info(f"User already exists: {user.email}")
            
        # 3. Create License
        statement = select(License).where(License.organization_id == org.id)
        license_obj = session.exec(statement).first()
        
        if not license_obj:
            license_obj = License(
                organization_id=org.id,
                tier=LicenseTier.BUSINESS,
                max_locations=5,
                max_users=50,
                max_devices=10,
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=365),
                is_active=True,
                license_key=str(uuid.uuid4()).upper(),
                addon_modules=["camera_ai", "access_control"]
            )
            session.add(license_obj)
            session.commit()
            session.refresh(license_obj)
            logger.info(f"Created License: {license_obj.license_key}")
        else:
            logger.info(f"License already exists for org")

        print("\n" + "="*50)
        print("CREDENCIALES DE PRUEBA GENERADAS")
        print("="*50)
        print(f"Organization: {org.name}")
        print(f"User Email:   {email}")
        print(f"Password:     {password}")
        print(f"License Key:  {license_obj.license_key}")
        print("="*50 + "\n")

def main() -> None:
    create_test_data()

if __name__ == "__main__":
    main()
