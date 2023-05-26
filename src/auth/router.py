from typing import Annotated, Any

from fastapi import APIRouter, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.schemas import UserRead, UserCreate, Token
from auth.utils import get_hashed_password
from database import get_async_session

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
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
    if db_response_user_exist:
        users_in_db = db_response_user_exist.scalars()
        for user_in_db in users_in_db:
            if user_in_db.username == user.username:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail='User with that username already exists')
            elif user_in_db.email == user.email:
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


@router.post('/login')
async def login_user(
        response: Response,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    pass

# @router.get('/users/me/', response_model=UserRead)
# async def get_current_user(
#         current_user: Annotated[UserRead, Depends(get_current_user)]
# ) -> UserRead:
#     return current_user


# @router.post('/users/login', response_model=Token)
# async def login_for_access_token(
#         session: Annotated[AsyncSession, Depends(get_async_session)],
#         form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ):
#     user = await authenticate_user(session=session, username=form_data.username, password=form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail='Incorrect username or password',
#             headers={'WWW-Authenticate': 'Bearer'}
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={'sub': user.username},
#         expires_delta=access_token_expires
#     )
#     return {'access_token': access_token, 'token_type': 'bearer'}
