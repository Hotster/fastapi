from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth.redis_db import RedisConnection
from auth.revoked_jwt_tokens import RedisJWTTokenRevocationService
from auth.schemas import Token, RefreshToken
from auth.utils import authenticate_user, get_access_token, get_refresh_token, decode_jwt_refresh_token, get_user_by_id
from database import get_async_session

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

redis_connection = RedisConnection()


@router.post('/login', response_model=Token)
async def login_user(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await authenticate_user(session=session,
                                   username=form_data.username,
                                   password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            headers={'WWW-Authenticate': 'Bearer'},
                            detail='Incorrect username or password')

    access_token = get_access_token(data=user.id)
    refresh_token = get_refresh_token(data=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='Bearer'
    )


@router.post('/refresh_tokens')
async def refresh_tokens(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        redis_client: Annotated[Redis, Depends(redis_connection.get_client)],
        token: Annotated[RefreshToken, Body()]
) -> Token:
    payload = decode_jwt_refresh_token(token.refresh_token)
    token_id = payload.get('jti')

    user = await get_user_by_id(session=session, user_id=payload.get('sub'))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User does not exist'
        )

    redis_service = RedisJWTTokenRevocationService(redis_client)
    is_token_revoked = await redis_service.is_token_revoked(token_id=token_id)
    if is_token_revoked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Refresh token revoked'
        )
    await redis_service.add_revoked_token(token_id=token_id)

    access_token = get_access_token(data=user.id)
    refresh_token = get_refresh_token(data=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='Bearer'
    )
