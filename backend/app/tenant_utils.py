from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, UserCreate

def create_tenant_db(db_name: str) -> None:
    """
    Create a new database in PostgreSQL.
    """
    # Use the administrative database to create a new one
    admin_url = str(settings.SQLALCHEMY_DATABASE_URI).replace(f"/{settings.POSTGRES_DB}", "/postgres")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE {db_name}"))
    engine.dispose()

def init_tenant_db(db_name: str, organization_data: dict) -> None:
    """
    Initialize the tenant database and seed it with organization info.
    """
    tenant_url = str(settings.SQLALCHEMY_DATABASE_URI).replace(f"/{settings.POSTGRES_DB}", f"/{db_name}")
    engine = create_engine(tenant_url)
    SQLModel.metadata.create_all(engine)
    
    # Seed organization
    from app.models import Organization
    with Session(engine) as session:
        org = Organization.model_validate(organization_data)
        session.add(org)
        session.commit()
    engine.dispose()

def create_tenant_superuser(db_name: str, email: str, password: str) -> None:
    """
    Create the initial superuser in the tenant database.
    """
    tenant_url = str(settings.SQLALCHEMY_DATABASE_URI).replace(f"/{settings.POSTGRES_DB}", f"/{db_name}")
    engine = create_engine(tenant_url)
    with Session(engine) as session:
        user_in = UserCreate(
            email=email,
            password=password,
            is_superuser=True,
            full_name="Organization Admin"
        )
        user = User.model_validate(
            user_in, 
            update={"hashed_password": get_password_hash(user_in.password)}
        )
        session.add(user)
        session.commit()
    engine.dispose()

def get_tenant_session(db_name: str) -> Session:
    """
    Get a session for a specific tenant database.
    """
    tenant_url = str(settings.SQLALCHEMY_DATABASE_URI).replace(f"/{settings.POSTGRES_DB}", f"/{db_name}")
    engine = create_engine(tenant_url)
    return Session(engine)
