import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import (
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    License,
    LicenseCreate,
    LicensePublic,
    LicensesPublic,
    LicenseUpdate,
    Message,
)

router = APIRouter(prefix="/licenses", tags=["licenses"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=LicensesPublic,
)
def read_licenses(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve licenses (Superuser only).
    """
    count_statement = select(func.count()).select_from(License)
    count = session.exec(count_statement).one()

    statement = select(License).offset(skip).limit(limit)
    licenses = session.exec(statement).all()

    return LicensesPublic(data=licenses, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=LicensePublic,
)
def create_license(
    *, session: SessionDep, license_in: LicenseCreate
) -> Any:
    """
    Create new license (Superuser only).
    """
    license = License.model_validate(license_in)
    session.add(license)
    session.commit()
    session.refresh(license)
    return license


@router.get(
    "/{license_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=LicensePublic,
)
def read_license(
    *, session: SessionDep, license_id: uuid.UUID
) -> Any:
    """
    Get license by ID (Superuser only).
    """
    license = session.get(License, license_id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    return license


@router.patch(
    "/{license_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=LicensePublic,
)
def update_license(
    *,
    session: SessionDep,
    license_id: uuid.UUID,
    license_in: LicenseUpdate,
) -> Any:
    """
    Update a license (Superuser only).
    """
    license = session.get(License, license_id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    update_data = license_in.model_dump(exclude_unset=True)
    license.sqlmodel_update(update_data)
    session.add(license)
    session.commit()
    session.refresh(license)
    return license


@router.delete(
    "/{license_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_license(
    *, session: SessionDep, license_id: uuid.UUID
) -> Any:
    """
    Delete a license (Superuser only).
    """
    license = session.get(License, license_id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
        
    session.delete(license)
    session.commit()
    return Message(message="License deleted successfully")
