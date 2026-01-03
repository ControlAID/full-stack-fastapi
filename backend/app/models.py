import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import EmailStr
from sqlalchemy import JSON, Column, String
from sqlmodel import Field, Relationship, SQLModel


# User Roles
class UserRole(str, Enum):
    ADMIN = "admin"        # Organization Admin
    STAFF = "staff"        # Security, Reception, etc.
    RESIDENT = "resident"  # End user, Employee, Resident
    VISITOR = "visitor"    # Temporary access

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.RESIDENT, sa_column=Column(String))
    organization_id: Optional[uuid.UUID] = Field(default=None, foreign_key="organization.id")
    unit_id: Optional[uuid.UUID] = Field(default=None, foreign_key="organizationunit.id")
    
    # Family/Employee hierarchy
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    is_primary_unit_user: bool = Field(default=False) # Head of household / Manager


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.RESIDENT)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)
    organization_id: Optional[uuid.UUID] = Field(default=None)
    role: UserRole | None = Field(default=None)
    is_active: bool | None = Field(default=None)
    unit_id: Optional[uuid.UUID] = Field(default=None)
    parent_id: Optional[uuid.UUID] = Field(default=None)
    is_primary_unit_user: bool | None = Field(default=None)

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    organization: Optional["Organization"] = Relationship(back_populates="users")
    unit: Optional["OrganizationUnit"] = Relationship(back_populates="users")
    
    parent: Optional["User"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "User.id"}
    )
    children: list["User"] = Relationship(back_populates="parent")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    organization_name: str | None = None
    organization_id: uuid.UUID | None = None
    unit_name: str | None = None


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
class OrganizationType(str, Enum):
    RESIDENTIAL = "residential"
    OFFICE = "office"
    COMMERCIAL = "commercial"
    PARKING = "parking"
    PRIVATE = "private"

class OrganizationBase(SQLModel):
    name: str = Field(index=True)
    type: OrganizationType = Field(default=OrganizationType.COMMERCIAL, sa_column=Column(String))
    address: str
    contact_email: str
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=128)

class OrganizationUpdate(SQLModel):
    name: str | None = None
    type: OrganizationType | None = None
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
    units: list["OrganizationUnit"] = Relationship(back_populates="organization")

class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    db_name: str | None = None
    created_at: datetime

class OrganizationsPublic(SQLModel):
    data: list[OrganizationPublic]
    count: int

# Organization Unit (Apartments, Offices, etc.)
class OrganizationUnitBase(SQLModel):
    name: str  # e.g "Apt 101", "Office 2B"
    type: str  # e.g "apartment", "office", "parking_spot"
    
class OrganizationUnitCreate(OrganizationUnitBase):
    organization_id: uuid.UUID

class OrganizationUnitUpdate(SQLModel):
    name: str | None = None
    type: str | None = None
    related_unit_id: uuid.UUID | None = None

class OrganizationUnit(OrganizationUnitBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id")
    organization: Organization = Relationship(back_populates="units")
    
    # Self-referential relationship for Parking linked to Apt
    related_unit_id: Optional[uuid.UUID] = Field(default=None, foreign_key="organizationunit.id")
    related_unit: Optional["OrganizationUnit"] = Relationship(
        sa_relationship_kwargs={"remote_side": "OrganizationUnit.id"}
    )
    
    # Residents/Users in this unit
    users: list["User"] = Relationship(back_populates="unit")

class OrganizationUnitPublic(OrganizationUnitBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    related_unit_id: uuid.UUID | None = None

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
    created_at: datetime = Field(default_factory=datetime.utcnow)

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


class AuditLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    action: str
    target: str
    details: str | None = None
    level: str = Field(default="info")  # info, warning, error, success
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str | None = None
    
    # Track which organization this action belongs to, if applicable
    organization_id: Optional[uuid.UUID] = Field(default=None, foreign_key="organization.id")


class LogPublic(SQLModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    action: str
    target: str
    details: str | None
    level: str
    timestamp: datetime
    ip_address: str | None
    organization_id: Optional[uuid.UUID]


class LogsPublic(SQLModel):
    data: list[LogPublic]
    count: int

class SystemCounts(SQLModel):
    organizations: int
    organizations_growth: float
    users: int
    users_growth: float
    licenses: int
    licenses_growth: float


class SystemMetrics(SQLModel):
    cpu_usage: float
    memory_usage: float
    db_status: str
    counts: SystemCounts
    timestamp: datetime


class ModulePublic(SQLModel):
    name: str
    version: str
    description: str
    author: str
    license_required: bool
    is_external: bool


class ModulesPublic(SQLModel):
    data: list[ModulePublic]
