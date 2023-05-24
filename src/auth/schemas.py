from uuid import UUID

from pydantic import BaseModel, validator


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    re_password: str


    @validator('re_password')
    @classmethod
    def check_re_password(cls, value):
        if value != cls.password:
            raise ValueError("Passwords don't match")
        return value


class UserRead(UserBase):
    id: UUID

    class Config:
        orm_mode = True
