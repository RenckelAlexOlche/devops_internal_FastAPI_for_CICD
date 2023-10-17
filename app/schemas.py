from fastapi import Form
from pydantic import BaseModel, validator
from app.validators import password_check, username_check

from app.models import Role


class TokenData(BaseModel):
    id: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(''),
        password: str = Form('')
        ) -> 'UserCreate':
        return cls(
            username=username, 
            password=password
        )

class UserBase(BaseModel):
    username: str
    full_name: str | None = None

class UserCreate(UserBase):
    password: str

    def validate_password(user: 'UserCreate') -> None:
        password_check(user.password, skip_specific_literals=True)

    def validate_username(user: 'UserCreate') -> None:
        username_check(user.username)

    @classmethod
    def as_form(
        cls,
        username: str = Form(''),
        full_name: str = Form(''),
        password: str = Form('')
        ) -> 'UserCreate':
        return cls(
            username=username, 
            full_name=full_name,
            password=password
        )

class User(UserBase):
    id: str
    roles: list[str] = []

    @validator('roles', pre=True, each_item=True)
    def get_roles_names(cls, role):
        if isinstance(role, Role):
            return role.name
        return role


    class Config:
        orm_mode = True



class TaskBase(BaseModel):
    title: str
    content: str

class TaskCreate(TaskBase):
    pass

    @classmethod
    def as_form(
        cls,
        title: str = Form(''),
        content: str = Form('')
        ) -> 'TaskCreate':
        return cls(
            title=title, 
            content=content
        )

class Task(TaskBase):
    id: int
    owner: User

    class Config:
        orm_mode = True
