import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    OrganizationUnit,
    OrganizationUnitCreate,
    OrganizationUnitPublic,
    OrganizationUnitUpdate,
)

router = APIRouter(prefix="/units", tags=["units"])

@router.get("/", response_model=list[OrganizationUnitPublic])
def read_units(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve units for current user's organization.
    """
    if not current_user.organization_id:
        return []

    statement = (
        select(OrganizationUnit)
        .where(OrganizationUnit.organization_id == current_user.organization_id)
        .offset(skip)
        .limit(limit)
    )
    result = session.exec(statement).all()
    # Explicitly map to Public model to verify related_unit_id is passed? 
    # SQLModel response_model handles it if field matches.
    return result

@router.post("/", response_model=OrganizationUnitPublic)
def create_unit(
    *, session: SessionDep, unit_in: OrganizationUnitCreate, current_user: CurrentUser
) -> Any:
    """
    Create new unit (Apartment, Office, etc).
    """
    if current_user.is_superuser:
         # simple check, superuser must specify org_id in body if they want, 
         # but usually superuser acts as admin.
         pass
    else:
        if not current_user.organization_id:
             raise HTTPException(status_code=400, detail="User not part of an organization")
        
        # Enforce org_id to be current user's org
        if unit_in.organization_id != current_user.organization_id:
             raise HTTPException(status_code=403, detail="Cannot create unit for another organization")

    unit = OrganizationUnit.model_validate(unit_in)
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit

@router.put("/{unit_id}", response_model=OrganizationUnitPublic)
def update_unit(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    unit_id: uuid.UUID,
    unit_in: OrganizationUnitUpdate,
) -> Any:
    """
    Update a unit.
    """
    unit = session.get(OrganizationUnit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
        
    if not current_user.is_superuser and unit.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = unit_in.model_dump(exclude_unset=True)
    unit.sqlmodel_update(update_data)
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit

@router.delete("/{unit_id}", response_model=Message)
def delete_unit(
    *, session: SessionDep, current_user: CurrentUser, unit_id: uuid.UUID
) -> Any:
    """
    Delete a unit.
    """
    unit = session.get(OrganizationUnit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
        
    if not current_user.is_superuser and unit.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if used by users?
    # Relationship allows cascade or set null, typically we might want to warn.
    # For now, let DB constraints handle logic, currently no cascade specified in model so it might block if FK exists.
    
    session.delete(unit)
    session.commit()
    return Message(message="Unit deleted successfully")
