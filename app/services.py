import os
import time
from uuid import uuid4
import bcrypt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, crud


#jwt_secret = os.environ.get('JWT_SECRET', 'secret')

class UserService:
    
    def add_to_role(db: Session, user_id: str, role_name: str) -> schemas.User:
        user: models.User = crud.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
            status_code = 404,
            detail      = [{'title': 'InvalidUserID', 'description': 'No user with this id was found'}]
            )
        role: models.Role = crud.get_role_by_name(db, role_name)
        if role is None:
            crud.create_role(db, models.Role(name = role_name))
            role: models.Role = crud.get_role_by_name(db, role_name)


        return schemas.User.from_orm(crud.add_user_role(db, user, role))

    
    def register(db: Session, user: schemas.UserCreate) -> schemas.User:

        if crud.get_user_by_username(db, user.username):
            raise HTTPException(
            status_code = 400,
            detail      = [{'title': 'InvalidUsername', 'description': 'User with that username already exists'}]
            )

        hashed_password = bcrypt.hashpw(bytes(user.password, 'UTF-8'), bcrypt.gensalt())
        db_user = models.User(
            id              = str(uuid4()),
            username        = user.username,
            full_name       = user.full_name, 
            hashed_password = hashed_password
            )

        return schemas.User.from_orm(crud.create_user(db, db_user))

    def login(db: Session, user_login: schemas.UserLogin) -> str:

        user = crud.get_user_by_username(db, user_login.username)

        if user is None:
            raise HTTPException(
            status_code = 400,
            detail      = [{'title': 'InvalidLogin', 'description': 'Incorrect username or password'}]
            )

        if not bcrypt.checkpw(user_login.password.encode('UTF-8'), bytes(str(user.hashed_password), 'UTF-8')):

            raise HTTPException(
            status_code = 400,
            detail      = [{'title': 'InvalidLogin', 'description': 'Incorrect username or password'}]
            )

        jwt_res = crud.create_access_token({'id': user.id, 'role': user.roles[0].name, 'iat': int(time.time())})


        return jwt_res

        
        
class TaskService:

    def create_task(db: Session, task: schemas.TaskCreate, owner_id: str) -> schemas.Task:

        db_task = models.Task(
            title           = task.title,
            content         = task.content
            )

        return schemas.Task.from_orm(crud.create_task(db, db_task, owner_id))
