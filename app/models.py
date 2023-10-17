from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base


users_roles = Table(
    "users_roles",
    Base.metadata,
    Column("user", ForeignKey("users.id"), primary_key=True),
    Column("role", ForeignKey("roles.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, default=str(uuid4()))
    username = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)

    roles = relationship("Role", secondary=users_roles, back_populates="users")

    tasks = relationship("Task", back_populates="owner")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)

    users = relationship("User", secondary=users_roles, back_populates="roles")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    content = Column(Text, nullable=False)

    owner_id = Column(String(36), ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")
