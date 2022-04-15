from typing import List

from fastapi import FastAPI, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette import status

import crud
import models
import schemas
from db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------auth region----------

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(db: Session, email: str):
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail={"message": "Common Unexpected Error"})


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, crud.SECRET_KEY, algorithms=[crud.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = schemas.TokenData(email=email)
        except JWTError:
            raise credentials_exception
        user = get_user(db=db, email=token_data.email)
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail={"message": "Invalid Credentials"})


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    try:
        return current_user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail={"message": "Invalid Credentials"})


# -------------end auth region----------


# -------------user region----------
@app.post("/user/signup/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    is_user = crud.check_user(user.email, db)
    if is_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/user/login/", response_model=schemas.Token)
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    user_obj = crud.authenticate_user(db, email=user.email, password=user.password)
    return crud.validate_user(user_obj)


# -------------user region----------


# -------------address_book region-----------------
@app.post("/address/", status_code=status.HTTP_201_CREATED)
def post_address(address: schemas.Address, db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(get_current_active_user)
                 ):
    return crud.create_address(db=db, address=address, current_user=current_user)


@app.get("/address/{radius}/{latitude}/{longitude}/", response_model=List[schemas.Address])
def read_address(radius: int, latitude: str, longitude: str, db: Session = Depends(get_db),
                 current_user: schemas.ReadUser = Depends(get_current_active_user)
                 ):
    return crud.get_address(db=db, current_user=current_user, radius=radius,
                            latitude=latitude, longitude=longitude)

# -------------end of address_book region-----------------
