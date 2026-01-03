import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import EmailStr
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    organization_id: Optional[uuid.UUID] = Field(default=None, foreign_key="organization.id")


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)
    organization_id: Optional[uuid.UUID] = Field(default=None)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    organization: Optional["Organization"] = Relationship(back_populates="users")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    organization_name: str | None = None
    organization_id: uuid.UUID | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# --- Security System Models ---

# Organization Models
class OrganizationBase(SQLModel):
    name: str = Field(index=True)
    type: str  # residential, office, commercial
    address: str
    contact_email: str
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=128)

class OrganizationUpdate(SQLModel):
    name: str | None = None
    type: str | None = None
    address: str | None = None
    contact_email: str | None = None
    is_active: bool | None = None

class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    db_name: str | None = Field(default=None)
    
    users: list["User"] = Relationship(back_populates="organization")
    licenses: list["License"] = Relationship(back_populates="organization")
    access_points: list["AccessPoint"] = Relationship(back_populates="organization")

class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    db_name: str | None = None
    created_at: datetime

class OrganizationsPublic(SQLModel):
    data: list[OrganizationPublic]
    count: int

# License Models
class LicenseTier(str, Enum):
    STARTER = "starter"      # 1 location, QR basic
    BUSINESS = "business"    # Multiple locations, QR + Face
    ENTERPRISE = "enterprise" # Unlimited, All included

class LicenseBase(SQLModel):
    tier: LicenseTier
    addon_modules: List[str] = Field(default=[], sa_column=Column(JSON))
    max_locations: int
    max_users: int
    max_devices: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True
    license_key: str = Field(unique=True, index=True)

class LicenseCreate(LicenseBase):
    organization_id: uuid.UUID
    license_key: str | None = Field(default=None, unique=True, index=True)

class LicenseUpdate(SQLModel):
    tier: LicenseTier | None = None
    max_locations: int | None = None
    max_users: int | None = None
    max_devices: int | None = None
    valid_until: datetime | None = None
    is_active: bool | None = None
    addon_modules: List[str] | None = None

class License(LicenseBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id")
    organization: Organization = Relationship(back_populates="licenses")

class LicensePublic(LicenseBase):
    id: uuid.UUID
    organization_id: uuid.UUID

class LicensesPublic(SQLModel):
    data: list[LicensePublic]
    count: int

# Access Point Models
class AccessPointBase(SQLModel):
    name: str
    location: str
    device_id: str = Field(index=True)
    enabled_modules: List[str] = Field(default=[], sa_column=Column(JSON))
    is_active: bool = True

class AccessPointCreate(AccessPointBase):
    organization_id: uuid.UUID

class AccessPointUpdate(SQLModel):
    name: str | None = None
    location: str | None = None
    enabled_modules: List[str] | None = None
    is_active: bool | None = None

class AccessPoint(AccessPointBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id")
    organization: Organization = Relationship(back_populates="access_points")

class AccessPointPublic(AccessPointBase):
    id: uuid.UUID
    organization_id: uuid.UUID


class AccessEvent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id")
    access_point_id: uuid.UUID = Field(foreign_key="accesspoint.id")
    
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    method: str  # qr, face, voice, manual
    status: str  # granted, denied
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    event_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
