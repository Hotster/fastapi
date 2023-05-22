from uuid import UUID

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: Field(str, min_length=3, max_length=50)
    email: Field(str, min_length=3, max_length=250)


class UserCreate(UserBase):
    password: Field(str, min_length=8, max_length=50)


class User(UserBase):
    id: UUID
