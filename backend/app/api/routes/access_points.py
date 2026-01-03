import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import func, select

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    AccessPoint,
    AccessPointCreate,
    AccessPointPublic,
    AccessPointUpdate,
    License,
    Message,
    Organization,
)

router = APIRouter(prefix="/access-points", tags=["access-points"])


@router.get(
    "/",
    # dependencies=[Depends(get_current_active_superuser)], # Removed strict superuser dependency
    response_model=list[AccessPointPublic],
)
def read_access_points(
    session: SessionDep, 
    current_user: CurrentUser,
    skip: int = 0, 
    limit: int = 100,
    device_id: str | None = None
) -> Any:
    """
    Retrieve access points. 
    - Superusers can see all.
    - Organization admins/users see only their organization's APs.
    """
    if current_user.is_superuser:
        statement = select(AccessPoint)
    else:
        statement = select(AccessPoint).where(AccessPoint.organization_id == current_user.organization_id)
    
    if device_id:
        statement = statement.where(AccessPoint.device_id == device_id)
        
    statement = statement.offset(skip).limit(limit)
    access_points = session.exec(statement).all()
    return access_points


@router.get("/{access_point_id}", response_model=AccessPointPublic)
def read_access_point(
    access_point_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get access point by ID.
    """
    access_point = session.get(AccessPoint, access_point_id)
    if not access_point:
        raise HTTPException(status_code=404, detail="Access point not found")
    
    if not current_user.is_superuser and current_user.organization_id != access_point.organization_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    return access_point


@router.post("/", response_model=AccessPointPublic)
def create_access_point(
    *, session: SessionDep, access_point_in: AccessPointCreate, current_user: CurrentUser
) -> Any:
    """
    Create new access point.
    """
    if not current_user.is_superuser:
        if current_user.organization_id != access_point_in.organization_id:
             raise HTTPException(status_code=403, detail="Not enough privileges")

    # 1. Enforce License Limits (Max Devices)
    organization = session.get(Organization, access_point_in.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Get active license
    # Assuming one active license per org for simplicity, or taking the latest
    statement = select(License).where(
        License.organization_id == access_point_in.organization_id,
        License.is_active == True
    ).order_by(License.created_at.desc())
    active_license = session.exec(statement).first()

    if not active_license:
        # If no active license, potentially block or allow restricted? 
        # Blocking for strict control.
        # Check if superuser to bypass? No, let's enforce.
        raise HTTPException(status_code=403, detail="Organization has no active license")
    
    # Count existing devices
    count_statement = select(func.count()).select_from(AccessPoint).where(
        AccessPoint.organization_id == access_point_in.organization_id
    )
    current_device_count = session.exec(count_statement).one()

    if current_device_count >= active_license.max_devices:
        raise HTTPException(
            status_code=403, 
            detail=f"License limit reached. Max devices: {active_license.max_devices}"
        )

    # 2. Create Access Point
    access_point = AccessPoint.model_validate(access_point_in)
    session.add(access_point)
    session.commit()
    session.refresh(access_point)
    return access_point


@router.patch("/{access_point_id}", response_model=AccessPointPublic)
def update_access_point(
    *,
    session: SessionDep,
    access_point_id: uuid.UUID,
    access_point_in: AccessPointUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update an access point.
    """
    access_point = session.get(AccessPoint, access_point_id)
    if not access_point:
        raise HTTPException(status_code=404, detail="Access point not found")
        
    if not current_user.is_superuser and current_user.organization_id != access_point.organization_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    # Verify Module Access if enabling modules
    if access_point_in.enabled_modules:
        statement = select(License).where(
            License.organization_id == access_point.organization_id,
            License.is_active == True
        ).order_by(License.created_at.desc())
        active_license = session.exec(statement).first()
        
        if not active_license:
             raise HTTPException(status_code=403, detail="Organization has no active license")
             
        # Check if all requested modules are in the license
        allowed_modules = set(active_license.addon_modules)
        requested_modules = set(access_point_in.enabled_modules)
        
        if not requested_modules.issubset(allowed_modules):
             missing = requested_modules - allowed_modules
             raise HTTPException(
                 status_code=403, 
                 detail=f"License does not allow these modules: {', '.join(missing)}"
             )

    update_data = access_point_in.model_dump(exclude_unset=True)
    access_point.sqlmodel_update(update_data)
    session.add(access_point)
    session.commit()
    session.refresh(access_point)
    return access_point


@router.delete("/{access_point_id}", response_model=Message)
def delete_access_point(
    *, session: SessionDep, access_point_id: uuid.UUID, current_user: CurrentUser
) -> Any:
    """
    Delete an access point.
    """
    access_point = session.get(AccessPoint, access_point_id)
    if not access_point:
        raise HTTPException(status_code=404, detail="Access point not found")
        
    if not current_user.is_superuser and current_user.organization_id != access_point.organization_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    session.delete(access_point)
    session.commit()
    return Message(message="Access point deleted successfully")
