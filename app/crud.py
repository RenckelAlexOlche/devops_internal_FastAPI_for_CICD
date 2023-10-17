from datetime import datetime, timedelta
import os
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import models

SECRET_KEY = os.environ.get('JWT_SECRET', 'secret')
ALGORITHM = "HS256"


def get_user_by_id(db: Session, id: str) -> models.User | None:
    return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(func.lower(models.User.username) == func.lower(username)).first()  


def add_user_role(db: Session, user: models.User, role: models.Role) -> models.User:
    user.roles.append(role)
    db.commit()
    db.refresh(user)
    return user

def create_user(db: Session, user: models.User) -> models.User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_role(db: Session, role: models.Role) -> models.Role:
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def get_role_by_name(db: Session, name: str) -> models.Role:
    return db.query(models.Role).filter(models.Role.name == name).first() 


def create_task(db: Session, task: models.Task, owner_id: str) -> models.Task:
    task.owner_id = owner_id
    db.add(task)
    db.commit()
    db.refresh(task)
    return task







def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# add comment for push
