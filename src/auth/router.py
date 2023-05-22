from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from database import get_async_session

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.get('/users/')
async def get_users(session: AsyncSession = Depends(get_async_session)):
    query = select(User)
    result = await session.execute(query)
    # return result.all()
    return