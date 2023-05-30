from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import JWT_ACCESS_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from database import get_async_session
from users.models import User

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 60  # 60 days

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

auth_scheme = HTTPBearer()


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password, hashed_password):
    return password_context.verify(password, hashed_password)


async def get_user_by_id(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user_id: str
) -> User | None:
    query = select(User).filter(User.id == user_id)
    db_response = await session.execute(query)
    user = db_response.scalar()

    if user is None:
        return None
    return user


async def get_user_by_username(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        username: str
) -> User | None:
    query = select(User).filter(User.username == username)
    db_response = await session.execute(query)
    user = db_response.scalar()

    if user is None:
        return None
    return user


def decode_jwt_token(token: str, secret: str):
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token has expired',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return payload


def decode_jwt_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token has expired',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return payload


def decode_jwt_refresh_token(token: str):
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token has expired',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return payload


async def get_current_user(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        token: Annotated[str, Depends(auth_scheme)]
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    payload = decode_jwt_access_token(token)
    user_id: str = payload.get('sub')
    if user_id is None:
        raise credential_exception
    user = get_user_by_id(session=session, user_id=user_id)
    if user is None:
        raise credential_exception
    return user


async def authenticate_user(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        username: str,
        password: str
) -> User | None:
    user = await get_user_by_username(session=session, username=username)

    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def get_access_token(data: str, expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {'exp': expires_delta, 'sub': str(data)}
    encoded_jwt = jwt.encode(to_encode, JWT_ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_refresh_token(data: str, expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {'exp': expires_delta, 'sub': str(data), 'jti': str(uuid4())}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
