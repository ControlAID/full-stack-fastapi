import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import col, delete, func, select


from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app import tenant_utils
from app.core.audit import log_action
from app.models import (
    Message,
    Organization,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=UsersPublic,
)
def read_users(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve users.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(User)
        count = session.exec(count_statement).one()
        statement = (
            select(User, Organization.name)
            .join(Organization, isouter=True)
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement).all()
        users = []
        for db_user, org_name in results:
            user_public = UserPublic.model_validate(db_user)
            user_public.organization_name = org_name
            users.append(user_public)
    else:
        # For organization admins, only show users in their organization
        count_statement = (
            select(func.count())
            .select_from(User)
            .where(User.organization_id == current_user.organization_id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(User, Organization.name)
            .join(Organization)
            .where(col(User.organization_id) == current_user.organization_id)
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement).all()
        users = []
        for db_user, org_name in results:
            user_public = UserPublic.model_validate(db_user)
            user_public.organization_name = org_name
            users.append(user_public)

    return UsersPublic(data=users, count=count)


@router.post(
    "/", response_model=UserPublic
)
def create_user(*, session: SessionDep, request: Request, user_in: UserCreate, current_user: CurrentUser) -> Any:
    """
    Create new user.
    """
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Multi-tenancy logic
    if not current_user.is_superuser:
        user_in.organization_id = current_user.organization_id
        user_in.is_superuser = False # Non-superusers cannot create superusers

    db_obj = User.model_validate(user_in, update={"hashed_password": get_password_hash(user_in.password)})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    user = db_obj

    # 2. Sync to tenant DB if applicable
    if user.organization_id:
        organization = session.get(Organization, user.organization_id)
        if organization and organization.db_name:
            try:
                with tenant_utils.get_tenant_session(organization.db_name) as tenant_session:
                    # Create the same user in tenant DB
                    tenant_user = User.model_validate(
                        user_in.model_dump(exclude_unset=True), 
                        update={
                            "id": user.id,
                            "hashed_password": db_obj.hashed_password
                        }
                    )
                    tenant_session.add(tenant_user)
                    tenant_session.commit()
            except Exception as e:
                # Log error but don't fail the whole request? 
                # Actually, for consistency it might be better to fail or log heavily.
                print(f"Failed to sync user to tenant DB: {e}")

    # Log user creation
    log_action(
        session=session,
        action="create",
        target="user",
        details=f"User {user.email} created",
        user=current_user,
        request=request
    )
    
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    db_obj = User.model_validate(user_create, update={"hashed_password": get_password_hash(user_create.password)})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    user = db_obj
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    request: Request,
    current_user: CurrentUser,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    # Permission check
    if not current_user.is_superuser:
        if db_user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have enough privileges to update this user",
            )
        
    user_data = user_in.model_dump(exclude_unset=True)
    if not current_user.is_superuser:
        # Non-superusers cannot change organization_id or is_superuser
        user_data.pop("organization_id", None)
        user_data.pop("is_superuser", None)

    if user_in.email:
        existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
        # Remove password from user_data as it's not a field in the User table model
        user_data.pop("password")
        
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Sync to tenant DB if applicable
    if db_user.organization_id:
        organization = session.get(Organization, db_user.organization_id)
        if organization and organization.db_name:
            try:
                with tenant_utils.get_tenant_session(organization.db_name) as tenant_session:
                    tenant_user = tenant_session.get(User, user_id)
                    if tenant_user:
                        tenant_user.sqlmodel_update(user_data, update=extra_data)
                        tenant_session.add(tenant_user)
                        tenant_session.commit()
                    else:
                        # If not found in tenant DB, recreate it
                        tenant_user = User.model_validate(
                            db_user.model_dump(exclude={"organization", "organization_name"}),
                            update={"hashed_password": db_user.hashed_password}
                        )
                        tenant_session.add(tenant_user)
                        tenant_session.commit()
            except Exception as e:
                print(f"Failed to sync user update to tenant DB: {e}")

    # Log user update
    log_action(
        session=session,
        action="update",
        target="user",
        details=f"User {db_user.email} updated",
        user=current_user,
        request=request
    )

    return db_user


@router.delete("/{user_id}")
def delete_user(
    session: SessionDep, request: Request, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        if db_user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403, detail="You don't have enough privileges"
            )
    if db_user == current_user:
        raise HTTPException(
            status_code=403, detail="Users are not allowed to delete themselves"
        )
    
    # Sync deletion to tenant DB if applicable
    if db_user.organization_id:
        organization = session.get(Organization, db_user.organization_id)
        if organization and organization.db_name:
            try:
                with tenant_utils.get_tenant_session(organization.db_name) as tenant_session:
                    tenant_user = tenant_session.get(User, user_id)
                    if tenant_user:
                        tenant_session.delete(tenant_user)
                        tenant_session.commit()
            except Exception as e:
                print(f"Failed to sync user deletion to tenant DB: {e}")

    # Log user deletion
    log_action(
        session=session,
        action="delete",
        target="user",
        details=f"User {db_user.email} deleted",
        user=current_user,
        request=request
    )

    session.delete(db_user)
    session.commit()
    return Message(message="User deleted successfully")
