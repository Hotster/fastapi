from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
# from auth.utils import get_current_user
from database import get_async_session
from tasks.schemas import TaskRead

router = APIRouter(
    prefix='/tasks',
    tags=['Tasks']
)

#
# @router.get('/', response_model=list[TaskRead] | Any)
# async def get_tasks(
#         session: Annotated[AsyncSession, Depends(get_async_session)],
#         current_user: Annotated[User, Depends(get_current_user)]
# ) -> list[TaskRead] | Any:
#     print(current_user)
#     return