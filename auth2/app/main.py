from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.models.user_db import UserDB, UserType
from app.db import get_session, create_db_and_tables
from sqlmodel import Session, select
from typing import Annotated, List


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(root_path="/api/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    type: UserType


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    type: UserType


@app.post("/register", response_model=UserOut)
def register(user: UserCreate, session: Session = Depends(get_session)):
    statement = select(UserDB).where(UserDB.email == user.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    user_db = UserDB(
        email=user.email, name=user.name, password=hashed_password, type=user.type
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return UserOut(
        id=user_db.id, email=user_db.email, name=user_db.name, type=user_db.type
    )


@app.post("/login", response_model=Token)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    statement = select(UserDB).where(UserDB.email == data.email)
    user_db = session.exec(statement).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not pwd_context.verify(data.password, user_db.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token_data = {"sub": user_db.email, "type": user_db.type}
    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserOut)
def read_users_me(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        statement = select(UserDB).where(UserDB.email == email)
        user_db = session.exec(statement).first()
        if user_db is None:
            raise HTTPException(status_code=401, detail="User not found")
        return UserOut(
            id=user_db.id, email=user_db.email, name=user_db.name, type=user_db.type
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/users", response_model=list[UserOut])
def get_users(session: Session = Depends(get_session)):
    users_db = session.exec(select(UserDB)).all()
    users = [
        UserOut(id=u.id, email=u.email, name=u.name, type=u.type) for u in users_db
    ]
    return users

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.get(UserDB, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user_db)
    session.commit()
    return
