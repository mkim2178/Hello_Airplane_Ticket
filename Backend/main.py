from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from datetime import datetime

import random


app = FastAPI()


EVERY_USER_DB_VERSION = []

EVERY_USER = []


@app.get("/")
async def root():
    return {"hello": "world"}


class User(BaseModel):
    user_id: str
    user_email: EmailStr | None = None


class UserInput(User):
    user_pswd: str
    user_age: int
    user_sex: str
    user_email: EmailStr | None = None
    user_membership: bool = False


class UserOutput(User):
    pass


class UserDB(User):
    hashed_pswd: str
    stored_date: datetime



def hash_the_password(user_password: str):

    alp_set = "abcdefghijklmnopqrstuvwxyz"
    hashed_string = "_"
    for i in range(3):
        hashed_string += random.choice(alp_set)

    return user_password + hashed_string


def save_user(user_input: UserInput):

    EVERY_USER.append(User(user_id=user_input.user_id, user_email=user_input.user_email))

    hashed_password = hash_the_password(user_input.user_pswd)
    user_in_db = UserDB(**user_input.dict(), hashed_pswd=hashed_password, stored_date=datetime.now())  # append user's info as an object (db version) into a list: EVERY_USER_DB_VERSION
    EVERY_USER_DB_VERSION.append(user_in_db)
    print("User is successfully saved!")
    return user_in_db


@app.post("/user/", response_model=UserOutput)
async def create_user(user_input: UserInput):
    user_saved = save_user(user_input)
    return user_saved


@app.get("/everyuser/")
async def read_every_user_in_db_version() -> list:  # this is a private info but I'm doing this as a practice (user's hashed password should not be shared)

    if not EVERY_USER:
        return ["There is no user"]



    return EVERY_USER



