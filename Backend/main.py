from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from datetime import datetime

import random


app = FastAPI()

EVERY_USER = []


@app.get("/")
async def root():
    """
    A simple root function that returns a dictionary.
    :return:
    """

    return {"hello": "world"}





class User(BaseModel):
    """
    User class only includes user's id and email (typing email is option: the default value is None).
    """

    user_id: str
    user_email: EmailStr | None = None


class UserInput(User):
    """
    UserInput class includes user's every specific info. The default of user_email and user_membership is None and False
    for each instance variables.
    """

    user_pswd: str
    user_age: int
    user_sex: str
    user_email: EmailStr | None = None
    user_membership: bool = False


class UserOutput(User):
    """
    UserOutput is just a dummy class; it's same as User.
    """
    pass


class UserDB(User):
    """
    UserDB also inherits from User class but additionally includes hashed password and the datetime module.
    """
    hashed_pswd: str
    stored_date: datetime



def hash_the_password(user_password: str):
    """
    A function that returns a hashed password.
    The new hashed password includes three random characters with original password that user defined.

    :param user_password: user's password
    :return: user's password + a string that has length 4 (ex: password123_vxr)
    """

    alp_set = "abcdefghijklmnopqrstuvwxyz"
    hashed_string = "_"
    for i in range(3):
        hashed_string += random.choice(alp_set) # randomly selects 3 alphabets from alp_set string

    return user_password + hashed_string



def save_user(user_input: UserInput):
    """
    A function that saves user's info into the EVERY_USER list.
    It returns a UserDB object (need additional explanation).

    :param user_input:
    :return:
    """

    EVERY_USER.append(User(user_id=user_input.user_id, user_email=user_input.user_email))

    hashed_password = hash_the_password(user_input.user_pswd)
    user_in_db = UserDB(**user_input.dict(), hashed_pswd=hashed_password, stored_date=datetime.now())  # append user's info as an object (db version) into a list: EVERY_USER_DB_VERSION
    print("User is successfully saved!")
    return user_in_db



@app.post("/user/", response_model=UserOutput)
async def create_user(user_input: UserInput):
    """
    Calls the save_user function to save user.
    Returns UserDB object.

    :param user_input:
    :return:
    """

    user_saved = save_user(user_input)
    return user_saved


@app.get("/everyuser/")
async def read_every_user_in_db_version() -> list:  # this is a private info but I'm doing this as a practice (user's hashed password should not be shared)
    """
    Returns a list that contains every user's id and email.
    If it's empty returns a list that contains a string: "There is no user".
    I will raise an Exception from this if statement (but for now, it will return an list that I explained from previous sentence).
    :return: list
    """

    if not EVERY_USER:
        return ["There is no user"]
    return EVERY_USER

