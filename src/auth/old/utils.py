from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic.schema import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.schemas import TokenData, UserInDB
from config import JWT_ACCESS_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from database import get_async_session

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 60  # 60 days

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/users/login')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_from_db(
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
):
    user = await get_user_from_db(session=session, username=username)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, JWT_ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, JWT_ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user_from_db(session=session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
