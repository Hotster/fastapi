from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from users.schemas import UserRead, UserCreate
from auth.utils import get_hashed_password
from database import get_async_session

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get('/users', response_model=Any)
async def get_users(
        session: AsyncSession = Depends(get_async_session)
) -> Any:
    query = select(User)
    db_response = await session.execute(query)
    users_in_db = db_response.scalars()

    return [UserRead.from_orm(user) for user in users_in_db]


@router.post('/users', response_model=UserRead)
async def create_user(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user: UserCreate
) -> UserRead:
    # Check if the user exists in db
    query_user_exists = select(User).filter(or_(User.username == user.username,
                                                User.email == user.email))
    db_response_user_exist = await session.execute(query_user_exists)
    user_from_db = db_response_user_exist.scalar()
    if user_from_db:
        if user_from_db.username == user.username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User with that username already exists')
        elif user_from_db.email == user.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User with that email already exists')

    # Create user
    hashed_password = get_hashed_password(user.password)
    stmt = insert(User).values(**user.dict(exclude={'password', 're_password'}),
                               password=hashed_password)
    await session.execute(stmt)
    await session.commit()

    query = select(User).where(User.username == user.username)
    db_response = await session.execute(query)
    created_user = db_response.scalar()

    return UserRead.from_orm(created_user)


@router.get('/users/{user_id}')
async def get_user(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user_id: str
) -> UserRead:
    query = select(User).filter(User.id == user_id)
    db_response = await session.execute(query)
    user = db_response.scalar()

    return UserRead.from_orm(user)
