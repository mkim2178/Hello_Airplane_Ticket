from datetime import datetime
from enum import Enum
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Annotated

import random


app = FastAPI()


EVERY_USER = {}
USER_DATABASE = []


class Tags(Enum):
    root = "Root"
    user = "User"




@app.get("/", tags=[Tags.root])
async def root():
    """
    A simple root function that returns a dictionary.
    """

    return {"hello": "world"}




class EmptyException(Exception):
    """
    An exception class when there is no user in the EMPTY_USER dictionary or USER_DATABASE list.
    """
    def __init__(self):
        self.message = f"Not enough user!"


@app.exception_handler(EmptyException)
async def empty_exception_handler(request: Request, exc: EmptyException):
    """
    - exc: an EmptyException object includes a message instance variable
    """
    return JSONResponse(status_code=418, content={"message": exc.message})


class InvalidUserIDException(Exception):
    """
    An exception class when the user input an invalid user id.
    If user's input id already exists in the EMPTY_USER dictionary OR if user's input id's 0th element is not alphabet,
    this exception will raise.
    """
    def __init__(self, user_id: str):
        self.user_id = user_id


@app.exception_handler(InvalidUserIDException)
async def invalid_or_duplicate_id(request: Request, exc: InvalidUserIDException):
    """
    - exc: an InvalidUserIDException object includes the invalid id as an instance variable.
    """
    return JSONResponse(
        status_code=418,
        content=f"You can't use the id: {exc.user_id} by one of the following reasons."
                f"-> Id already exists in the database."
                f"-> Invalid id format (your 0th character should be an alphabet)."
    )





class User(BaseModel):
    """
    User class only includes the user's id. This class will be used in the public.
    """
    user_id: str


class UserInput(User):
    """
    UserInput class includes user's every private information. The default of membership and email instance variables are None and False
    for each.

    - pswd: user's password
    - age: user's age
    - sex: user's sex
    - full_name: user's full name
    - is_vip: user's status (if true -> user is a vip)
    - email: user's email
    """

    pswd: str
    age: int
    sex: str
    full_name: str
    is_vip: bool = False
    email: EmailStr | None = None


class UserDB(User):
    """
    UserDB also inherits from User class but additionally includes hashed password and the datetime module.
    """

    hashed_pswd: str
    stored_date: datetime



def hash_the_password(user_password: str):
    """
    A function that returns a hashed password.
    The new hashed password includes a hyphen and additional three random characters with original password that user previously defined.
    """

    alp_set = "abcdefghijklmnopqrstuvwxyz"
    hashed_string = "_"
    for i in range(3):
        hashed_string += random.choice(alp_set) # randomly selects 3 alphabets from alp_set string

    return user_password + hashed_string



def save_user(user_input: UserInput):
    """
    A function that saves user's info into the EVERY_USER dict and USER_DATABASE list.
    If user inputs an invalid id, it will raise InvalidUserIDException.
    It returns the converted User object.
    """

    if user_input.user_id in EVERY_USER or not user_input.user_id[0].isalpha():
        raise InvalidUserIDException(user_input.user_id)

    user = User(user_id=user_input.user_id)
    EVERY_USER[user_input.user_id] = user_input.full_name
    hashed_password = hash_the_password(user_input.pswd)
    user_in_db = UserDB(**user_input.dict(), hashed_pswd=hashed_password, stored_date=datetime.now())  # append user's info as an object (db version) into a list: EVERY_USER_DB_VERSION
    USER_DATABASE.append(user_in_db)

    print("User is successfully saved!")

    return user



@app.post("/user/", response_model=User, tags=[Tags.user])
async def create_user(user_input: UserInput):
    """
    Calls the save_user function to save user.
    Returns UserDB object.
    """

    user_saved = save_user(user_input)
    return user_saved




@app.get("/user/", tags=[Tags.user])
async def read_every_user(version: str) -> dict | list | str:
    """
    This will return one of these data types (dict, list, str).
    If the version query is invalid, it will return a string: haha! check your query!
    Otherwise, it will return a dict or list that includes every user's information.
    """

    if version == "standard":
        return read_all(EVERY_USER)

    elif version == "database":
        return read_all(USER_DATABASE)

    else:
        return "haha! check your query"


def read_all(data):
    """
    If something is None (null) it will raise an EmptyException.
    Otherwise, it will just return something (bad parameter name (something): will change in the future).
    """

    if not data:
        raise EmptyException()
    return data







class SpecificRange:

    """
    SpecificRange includes 3 queries: q, start, and end.
    The asterisk exists because the first parameter q's default value is None, which is not allowed in python.
    """

    def __init__(self, *, q: str | None = None, start: int, end: int):

        self.q = q
        self.start = start
        self.end = end


@app.get("/readsomedatabase/", tags=[Tags.user])
async def read_some_database(several: Annotated[SpecificRange, Depends(SpecificRange)]):

    """
    Using Dependency to read certain amount of data that are stored in the database (list).
    If q exists, it will be included inside of response dictionary.
    Otherwise, it will only include several data and this will be determined by start and end queries.
    It returns a response dictionary.
    """

    response = {}

    if several.q:
        response.update({"q": several.q})

    users = USER_DATABASE[several.start: several.end]

    response.update({"users": users})

    return response

