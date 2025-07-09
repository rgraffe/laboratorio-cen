from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional

class UserType(str, Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    PROFESOR = "PROFESOR"
    ESTUDIANTE = "ESTUDIANTE"

class UserDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    password: str
    type: UserType
