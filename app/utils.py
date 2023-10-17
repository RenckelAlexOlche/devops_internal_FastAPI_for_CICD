from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app import crud
from app.crud import SECRET_KEY, ALGORITHM
from app.models import User
from app.schemas import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(db: Session, token: str) -> User:

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        user_role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id, role=user_role)

    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_id(db, token_data.id)

    if user is None:
        raise credentials_exception

    return user