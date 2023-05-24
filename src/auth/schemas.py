from pydantic import BaseModel, EmailStr, UUID4, validator


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    re_password: str

    @validator('re_password')
    def password_match(cls, value, values):
        if value != values.get('password'):
            raise ValueError("Passwords do not match")
        return value


class UserRead(UserBase):
    id: UUID4

    class Config:
        orm_mode = True
