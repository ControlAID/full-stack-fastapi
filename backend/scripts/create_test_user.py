import logging
import uuid
import sys
import time
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.core.db import engine
from app.core.security import get_password_hash
from app.models import (
    Organization, User, License, LicenseTier, AuditLog, AccessPoint, AccessEvent,
    OrganizationCreate, UserCreate, UserRole
)
from app import tenant_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data() -> None:
    # Use a loop to retry DB connection if starting up
    for _ in range(5):
        try:
            with Session(engine) as session:
                session.exec(select(User).limit(1))
                break
        except Exception:
            logger.info("Waiting for DB...")
            time.sleep(2)

    with Session(engine) as session:
        # 1. Cleaner approach: Check if org exists and delete it if it's broken (no db_name)
        org_name = "Test Security Corp"
        statement = select(Organization).where(Organization.name == org_name)
        org = session.exec(statement).first()
        
        email = "admin@testcorp.com"
        password = "password123"
        hashed_password = get_password_hash(password)

        if org:
            if not org.db_name:
                logger.warning(f"Organization {org.name} exists but has no db_name. Cleaning up...")
                
                # 1. Delete Access Events
                events_stmt = select(AccessEvent).where(AccessEvent.organization_id == org.id)
                events = session.exec(events_stmt).all()
                for event in events: session.delete(event)
                
                # 2. Delete Access Points
                aps_stmt = select(AccessPoint).where(AccessPoint.organization_id == org.id)
                aps = session.exec(aps_stmt).all()
                for ap in aps: session.delete(ap)

                # 3. Delete Users
                user_stmt = select(User).where(User.organization_id == org.id)
                user = session.exec(user_stmt).first()
                if user: 
                    # Delete AuditLogs for this user
                    logs_stmt = select(AuditLog).where(AuditLog.user_id == user.id)
                    logs = session.exec(logs_stmt).all()
                    for log in logs:
                        session.delete(log)
                    
                    session.delete(user)
                
                # 4. Delete License
                lic_stmt = select(License).where(License.organization_id == org.id)
                lic = session.exec(lic_stmt).first()
                if lic: session.delete(lic)
                
                # 5. Delete Org AuditLogs
                # Delete AuditLogs for this Organization (if any exist independently of user)
                # AuditLog has organization_id field
                org_logs_stmt = select(AuditLog).where(AuditLog.organization_id == org.id)
                org_logs = session.exec(org_logs_stmt).all()
                for log in org_logs:
                    session.delete(log)

                session.delete(org)
                session.commit()
                org = None
            else:
                logger.info(f"Organization already exists with DB: {org.db_name}")

        if not org:
            # Create NEW Organization
            # 1. Generate DB Name
            db_name = f"org_{uuid.uuid4().hex[:12]}"
            logger.info(f"Generated DB Name: {db_name}")
            
            # 2. Create Org Record
            org = Organization(
                name=org_name,
                type="commercial",
                address="123 Database St.",
                contact_email=email,
                is_active=True,
                db_name=db_name
            )
            session.add(org)
            session.commit()
            session.refresh(org)
            logger.info(f"Created Organization record: {org.name}")

            # 3. Provision Tenant DB
            try:
                # Check if DB exists? create_tenant_db just calls CREATE DATABASE, which fails if exists.
                # Assuming new name = new db.
                logger.info("Creating Tenant DB...")
                tenant_utils.create_tenant_db(db_name)
                
                logger.info("Initializing Tenant DB schema...")
                # We need to pass org data dict.
                org_data = org.model_dump()
                tenant_utils.init_tenant_db(db_name, org_data)
                
                logger.info("Creating Tenant Superuser...")
                tenant_utils.create_tenant_superuser(db_name, email, password)
                
            except Exception as e:
                logger.error(f"Failed to provision tenant DB: {e}")
                # Optional: Cleanup
                return

        # 2. Create/Update Admin User in MAIN DB (for Login)
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if not user:
            user = User(
                email=email,
                hashed_password=hashed_password,
                full_name="Admin Test",
                organization_id=org.id,
                is_superuser=False, # Tenant admin is not system superuser
                is_active=True,
                role=UserRole.ADMIN
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Created Main DB User: {user.email}")
        else:
            # Ensure links are correct if we recreated org
            if user.organization_id != org.id:
                user.organization_id = org.id
                session.add(user)
                session.commit()
            logger.info(f"User already exists: {user.email}")
            
        # 3. Create License (Main DB)
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
                addon_modules=["camera_ai", "access_control", "system_dashboard", "weather_connector"]
            )
            session.add(license_obj)
            session.commit()
            session.refresh(license_obj)
            logger.info(f"Created License: {license_obj.license_key}")
        else:
            logger.info(f"License already exists")

        print("\n" + "="*50)
        print("CREDENCIALES DE PRUEBA (ACTUALIZADAS)")
        print("="*50)
        print(f"Organization: {org.name}")
        print(f"DB Name:      {org.db_name}")
        print(f"User Email:   {email}")
        print(f"Password:     {password}")
        print(f"License Key:  {license_obj.license_key}")
        print("="*50 + "\n")

def main() -> None:
    create_test_data()

if __name__ == "__main__":
    main()
