import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    License,
    LicensesPublic,
    Message,
    Organization,
    OrganizationCreate,
    OrganizationPublic,
    OrganizationsPublic,
    OrganizationUpdate,
    User,
    UserCreate,
    UserPublic,
    UsersPublic,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=OrganizationsPublic,
)
def read_organizations(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve organizations (Available only for superusers).
    """
    count_statement = select(func.count()).select_from(Organization)
    count = session.exec(count_statement).one()

    statement = select(Organization).offset(skip).limit(limit)
    organizations = session.exec(statement).all()

    return OrganizationsPublic(data=organizations, count=count)


@router.get("/{organization_id}", response_model=OrganizationPublic)
def read_organization(
    organization_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get organization by ID.
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Access control: Superuser or member of the organization
    if not current_user.is_superuser and current_user.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    return organization


from app import tenant_utils

@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=OrganizationPublic,
)
def create_organization(
    *, session: SessionDep, organization_in: OrganizationCreate
) -> Any:
    """
    Create new organization (Superuser only).
    """
    # 1. Generate database name
    db_name = f"org_{uuid.uuid4().hex[:12]}"
    
    # 2. Create the organization record in the main DB
    org_data = organization_in.model_dump(exclude={"admin_email", "admin_password"})
    organization = Organization.model_validate(
        org_data, 
        update={"db_name": db_name}
    )
    session.add(organization)
    session.commit()
    session.refresh(organization)
    
    # 3. Create and initialize the tenant database
    try:
        tenant_utils.create_tenant_db(db_name)
        tenant_utils.init_tenant_db(db_name, organization.model_dump())
        
        # 4. Create the tenant superuser
        tenant_utils.create_tenant_superuser(
            db_name, 
            organization_in.admin_email, 
            organization_in.admin_password
        )

        # 5. Create the admin user in the main DB so they can login
        from app.core.security import get_password_hash
        user_in = UserCreate(
            email=organization_in.admin_email,
            password=organization_in.admin_password,
            is_superuser=True,
            full_name="Organization Admin",
            organization_id=organization.id,
        )
        user = User.model_validate(
            user_in, update={"hashed_password": get_password_hash(user_in.password)}
        )
        session.add(user)
        session.commit()
        
    except Exception as e:
        # If DB creation fails, we might want to delete the org record or log error
        # For now, just raise the exception
        session.delete(organization)
        session.commit()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create tenant environment: {str(e)}"
        )

    return organization


@router.patch("/{organization_id}", response_model=OrganizationPublic)
def update_organization(
    *,
    session: SessionDep,
    organization_id: uuid.UUID,
    organization_in: OrganizationUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update an organization.
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    if not current_user.is_superuser and current_user.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    update_data = organization_in.model_dump(exclude_unset=True)
    organization.sqlmodel_update(update_data)
    session.add(organization)
    session.commit()
    session.refresh(organization)
    return organization


@router.delete(
    "/{organization_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_organization(
    *, session: SessionDep, organization_id: uuid.UUID
) -> Any:
    """
    Delete an organization (Superuser only).
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    session.delete(organization)
    session.commit()
    return Message(message="Organization deleted successfully")


@router.get("/{organization_id}/users", response_model=UsersPublic)
def read_organization_users(
    organization_id: uuid.UUID, 
    session: SessionDep, 
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve users for a specific organization from its tenant DB.
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    if not current_user.is_superuser and current_user.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    if not organization.db_name:
        return UsersPublic(data=[], count=0)
        
    with tenant_utils.get_tenant_session(organization.db_name) as tenant_session:
        statement = select(User).offset(skip).limit(limit)
        users = tenant_session.exec(statement).all()
        
        count_statement = select(func.count()).select_from(User)
        count = tenant_session.exec(count_statement).one()
        
        # Convert to UserPublic before setting organization_name
        users_public = []
        for user in users:
            user_public = UserPublic.model_validate(user)
            user_public.organization_name = organization.name
            users_public.append(user_public)
            
        return UsersPublic(data=users_public, count=count)


@router.get("/{organization_id}/licenses", response_model=LicensesPublic)
def read_organization_licenses(
    organization_id: uuid.UUID, 
    session: SessionDep, 
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve licenses for a specific organization.
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    if not current_user.is_superuser and current_user.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    statement = select(License).where(License.organization_id == organization_id).offset(skip).limit(limit)
    licenses = session.exec(statement).all()
    
    count_statement = select(func.count()).select_from(License).where(License.organization_id == organization_id)
    count = session.exec(count_statement).one()
    
    return LicensesPublic(data=licenses, count=count)
