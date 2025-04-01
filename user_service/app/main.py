import logging
import bcrypt
import jwt
import os
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, EmailStr, constr, field_validator
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "123456")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

engine = create_engine("postgresql://user:password@db/users_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
app = FastAPI()
security = HTTPBearer()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    birth_date = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    first_name: constr(min_length=1, max_length=50)
    last_name: constr(min_length=1, max_length=50)
    birth_date: str
    phone: constr(min_length=10, max_length=15)

    @field_validator("phone")
    def validate_phone(cls, value):
        if not value.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError(
                "Phone number must contain only digits, '+', '-', or spaces"
            )
        return value

    @field_validator("birth_date")
    def validate_birth_date(cls, value):
        try:
            date = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Birth date must be in the format YYYY-MM-DD")

        if date > datetime.now():
            raise ValueError("Birth date cannot be in the future")

        return value


class UserAuth(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8)


class UserUpdate(BaseModel):
    first_name: constr(min_length=1, max_length=50)
    last_name: constr(min_length=1, max_length=50)
    birth_date: str
    phone: constr(min_length=10, max_length=15)

    @field_validator("phone")
    def validate_phone(cls, value):
        if not value.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError(
                "Phone number must contain only digits, '+', '-', or spaces"
            )
        return value

    @field_validator("birth_date")
    def validate_birth_date(cls, value):
        try:
            date = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Birth date must be in the format YYYY-MM-DD")

        if date > datetime.now():
            raise ValueError("Birth date cannot be in the future")

        return value


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_jwt_token(username: str):
    expiration = datetime.now() + timedelta(hours=1)
    payload = {"sub": username, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token: str):
    try:
        logger.info(f"Attempting to decode token: {token}")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Decoded payload: {payload}")

        return payload["sub"]
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token error: {e}")
        logger.error(f"Token provided: {token}")
        logger.error(f"Expected SECRET_KEY: {SECRET_KEY}")
        logger.error(f"Expected ALGORITHM: {ALGORITHM}")
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    username = decode_jwt_token(token)
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/register/")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        first_name=user.first_name,
        last_name=user.last_name,
        birth_date=user.birth_date,
        phone=user.phone,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}


@app.post("/login/")
def login(user: UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_jwt_token(db_user.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/profile/")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "birth_date": current_user.birth_date,
        "phone": current_user.phone,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
    }


@app.put("/profile/")
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Updating profile for {current_user.username}")
    logger.info(f"Received update data: {user_update}")

    current_user.first_name = user_update.first_name
    current_user.last_name = user_update.last_name
    current_user.birth_date = user_update.birth_date
    current_user.phone = user_update.phone
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully"}
