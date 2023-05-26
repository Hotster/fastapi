from datetime import datetime

from pydantic import BaseModel, UUID4,  Field


class TaskBase(BaseModel):
    id: UUID4
    name: str = Field(max_length=255)
    description: str = Field(default=None, max_length=1000)
    owner_id: UUID4


class TaskCreate(TaskBase):
    due_date: datetime | None


class TaskRead(TaskBase):
    created_at: datetime | None
    due_date: datetime | None
    done_at: datetime | None
