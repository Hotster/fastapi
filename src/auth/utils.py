from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.schemas import UserInDB
from config import JWT_ACCESS_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from database import get_async_session

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 60  # 60 days

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password, hashed_password):
    return password_context.verify(password, hashed_password)


async def get_user_from_db_by_username(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        username: str
) -> UserInDB | None:
    query = select(User).where(User.username == username)
    db_response = await session.execute(query)
    user_in_db = db_response.scalar()

    if user_in_db is None:
        return None
    return UserInDB.from_orm(user_in_db)


async def authenticate_user(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        username: str,
        password: str
) -> UserInDB | False:
    user = await get_user_from_db_by_username(session=session, username=username)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(user_id: str, expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {'exp': expires_delta, 'sub': user_id}
    encoded_jwt = jwt.encode(to_encode, JWT_ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str, expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {'exp': expires_delta, 'sub': user_id}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
