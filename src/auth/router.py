from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.schemas import UserRead, UserCreate
from database import get_async_session

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.get('/users/', response_model=Any)
async def get_users(
        session: AsyncSession = Depends(get_async_session)
) -> Any:
    query = select(User)
    result = await session.execute(query)
    users_db = result.scalars().all()

    return [UserRead.from_orm(user) for user in users_db]


@router.post('/users/', response_model=UserRead)
async def register_user(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user: UserCreate
) -> UserRead:
    user_dict = user.dict()
    user_dict.pop('re_password')

    stmt = insert(User).values(**user_dict)
    await session.execute(stmt)
    await session.commit()

    query = select(User).where(User.username == user.username)
    result = await session.execute(query)
    user_ib = result.scalar()

    return UserRead.from_orm(user_ib)
