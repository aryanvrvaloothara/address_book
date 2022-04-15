from datetime import timedelta, datetime
from typing import Optional

from fastapi import HTTPException
from fastapi.params import Depends
from geopy.distance import geodesic
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

import models
import schemas
from db import SessionLocal
from utils import log_exception

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

ALGORITHM = "HS256"


# -----------region auth --------


# -----------end region auth----------


# -------------region user------------------

def get_password_hash(password):
    try:
        return pwd_context.hash(password)
    except Exception as e:
        log_exception(e)
        raise HTTPException(status_code=400, detail={"message": "Unexpected error occurred"})


def check_user(email: str, db):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.User):
    try:
        db_user = models.User(name=user.name, email=user.email,
                              password=get_password_hash(user.password))
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except Exception as e:
        log_exception(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unexpected Error Occurred")


# -------------end region user------------------


# ------------region login------------
def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        log_exception(e)
        raise HTTPException(status_code=400, detail={"message": "Unexpected Error Occurred"})


def authenticate_user(db, email: str, password: str):
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user
    except Exception as e:
        log_exception(e)
        raise HTTPException(status_code=400, detail={"message": "Unexpected Error Occurred"})


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=300)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        log_exception(e)
        raise HTTPException(status_code=400, detail={"message": "Unexpected Error Occured"})


def validate_user(user_obj: models.User):
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        try:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user_obj.email}, expires_delta=access_token_expires
            )

            headers = {
                "access_token": access_token,
                "token_type": "bearer",
            }
            return JSONResponse(status_code=200, content=headers)
        except Exception as e:
            log_exception(e)
            raise HTTPException(status_code=400, detail={"message": "Login Failed"})


# ------------end region login-------------


# -----------region address-----------------
def create_address(db: Session, address: schemas.Address, current_user: schemas.User):
    try:
        db_activity = models.AddressBook(name=address.name, house_name=address.house_name, place=address.place,
                                         post_office=address.post_office, pin_code=address.pin_code,
                                         latitude=address.latitude, longitude=address.longitude,
                                         user_id=current_user.id
                                         )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity

    except Exception as e:
        log_exception(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unexpected Error Occurred")


def get_address(db: Session, current_user: schemas.ReadUser, radius, latitude, longitude):
    try:
        query_set = db.query(models.AddressBook).filter(models.AddressBook.user_id == current_user.id).all()
        # creates the new list of address within the input radius.
        new_query_set = [x for x in query_set if geodesic((x.latitude, x.longitude), (latitude, longitude)) <= radius]
        return new_query_set
    except Exception as e:
        log_exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unexpected Error Occurred")
