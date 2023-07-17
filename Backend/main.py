from enum import Enum

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)



class NotFoundException(Exception):

    def __init__(self, x: str):
        self.x = x



app = FastAPI()

# app.mount("/templates/TheRoot", StaticFiles(directory="TheRoot"), name="TheRoot")


templates = Jinja2Templates(directory="/Users/minwookim/Desktop/Hello_Airplane_Ticket/templates")




# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Tags(Enum):
    users = "Users"
    tickets = "Tickets"
    root = "Root"






@app.get("/", tags=[Tags.root])
async def root():
    return "ROOT"






def check_user(user_id: int, db: Session = Depends(get_db)):
    """
    * Logical Step

    1. call get_user function from crud file and store as db_user
    2. if db_user is None, raise an exception (This means the input user_id does not exist in our database)
    3. otherwise, return the user
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise NotFoundException(x="User")
    return db_user



def check_ticket(user_id: int, ticket_id: int, db: Session = Depends(get_db)):
    """
    * Logical Step

    1. call check_user function to check the validation of user_id
    2. call get_ticket_by_id function from crud file to check the validation of ticket_id
    3. if db_ticket is None, raise an exception (This means the input ticket_id does not exist in our database)
    4. otherwise, return the ticket
    """
    db_user = check_user(user_id, db)
    db_ticket = crud.get_ticket_by_id(db, db_user.id, ticket_id)

    if db_ticket is None:
        raise NotFoundException(x="Ticket")
    return db_ticket


def check_tickets(user_id: int, db: Session = Depends(get_db)):
    """
    * Logical Step

    same as check_ticket function but this time call get_every_ticket_by_id function from crud file
    """
    db_user = check_user(user_id, db)
    db_tickets = crud.get_every_ticket_by_id(db, user_id=db_user.id)
    if not db_tickets:
        raise NotFoundException(x="Tickets")
    return db_tickets







@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})






@app.exception_handler(NotFoundException)
async def user_not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content=f"{exc.x} not found!"
    )




@app.post("/users/", response_model=schemas.User, tags=[Tags.users])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)



@app.get("/users/", response_model=list[schemas.User], tags=[Tags.users])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User, tags=[Tags.users])
def read_user(user_id: int, db: Session = Depends(get_db)):
    return check_user(user_id, db)






@app.get("/testing/", tags=[Tags.users])
def testing_read_user(request: Request, user_id: int, db: Session = Depends(get_db)):

    db_user = check_user(user_id, db)

    # for ticket in db_user.tickets:
    #     print(ticket.id, ticket.destination, ticket.seat_level, ticket.seat_number, ticket.owner_id)

    return templates.TemplateResponse("item.html", {"request": request, "user_info": db_user})









@app.delete("/users/{user_id}", tags=[Tags.users])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = check_user(user_id, db)
    return crud.delete_user(db, user_id=db_user.id)



@app.post("/users/{user_id}/tickets/", response_model=schemas.Ticket, tags=[Tags.tickets])
def create_ticket_for_user(user_id: int, ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_user = check_user(user_id, db)
    return crud.create_user_ticket(db=db, ticket=ticket, user_id=db_user.id)




@app.get("/tickets/", response_model=list[schemas.Ticket], tags=[Tags.tickets])
def read_every_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tickets = crud.get_tickets(db, skip=skip, limit=limit)
    return tickets











@app.get("/tickets/{user_id}", response_model=schemas.Ticket, tags=[Tags.tickets])
def read_ticket_by_id(user_id: int, ticket_id: int, db: Session = Depends(get_db)):
    return check_ticket(user_id, ticket_id, db)


@app.get("/tickets/{user_id}/every-ticket", response_model=list[schemas.Ticket], tags=[Tags.tickets])
def read_every_ticket_by_id(user_id: int, db: Session = Depends(get_db)):
    return check_tickets(user_id, db)



@app.delete("/tickets/{user_id}/delete-ticket", tags=[Tags.tickets])
def delete_ticket_by_id(user_id: int, ticket_id: int, db: Session = Depends(get_db)):
    db_ticket = check_ticket(user_id, ticket_id, db)
    return crud.delete_ticket(db, user_id, db_ticket.id)


@app.delete("/tickets/{user_id}/delete-every-ticket", tags=[Tags.tickets])
def delete_every_ticket_by_id(user_id: int, db: Session = Depends(get_db)):
    db_tickets = check_tickets(user_id, db)
    return crud.delete_every_tickets(db, user_id)










































# practice area #


# from datetime import datetime
# from enum import Enum
# from fastapi import Depends, FastAPI, Request
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, EmailStr
# from typing import Annotated
#
# import random


# EVERY_USER = {}
# USER_DATABASE = []
#
#
# class Tags(Enum):
#     root = "Root"
#     user = "User"
#
#
# class EmptyException(Exception):
#     """
#     An exception class when there is no user in the EMPTY_USER dictionary or USER_DATABASE list.
#     """
#     def __init__(self):
#         self.message = f"Not enough user!"
#
#
# @app.exception_handler(EmptyException)
# async def empty_exception_handler(request: Request, exc: EmptyException):
#     """
#     - exc: an EmptyException object includes a message instance variable
#     """
#     return JSONResponse(status_code=418, content={"message": exc.message})
#
#
# class InvalidUserIDException(Exception):
#     """
#     An exception class when the user input an invalid user id.
#     If user's input id already exists in the EMPTY_USER dictionary OR if user's input id's 0th element is not alphabet,
#     this exception will raise.
#     """
#     def __init__(self, user_id: str):
#         self.user_id = user_id
#
#
# @app.exception_handler(InvalidUserIDException)
# async def invalid_or_duplicate_id(request: Request, exc: InvalidUserIDException):
#     """
#     - exc: an InvalidUserIDException object includes the invalid id as an instance variable.
#     """
#     return JSONResponse(
#         status_code=418,
#         content=f"You can't use the id: {exc.user_id} by one of the following reasons."
#                 f"-> Id already exists in the database."
#                 f"-> Invalid id format (your 0th character should be an alphabet)."
#     )
#
#
#
#
#
# class User(BaseModel):
#     """
#     User class only includes the user's id. This class will be used in the public.
#     """
#     user_id: str
#
#
# class UserInput(User):
#     """
#     UserInput class includes user's every private information. The default of membership and email instance variables are None and False
#     for each.
#
#     - pswd: user's password
#     - age: user's age
#     - sex: user's sex
#     - full_name: user's full name
#     - is_vip: user's status (if true -> user is a vip)
#     - email: user's email
#     """
#
#     pswd: str
#     age: int
#     sex: str
#     full_name: str
#     is_vip: bool = False
#     email: EmailStr | None = None
#
#
# class UserDB(User):
#     """
#     UserDB also inherits from User class but additionally includes hashed password and the datetime module.
#     """
#
#     hashed_pswd: str
#     stored_date: datetime
#
#
#
# def hash_the_password(user_password: str):
#     """
#     A function that returns a hashed password.
#     The new hashed password includes a hyphen and additional three random characters with original password that user previously defined.
#     """
#
#     alp_set = "abcdefghijklmnopqrstuvwxyz"
#     hashed_string = "_"
#     for i in range(3):
#         hashed_string += random.choice(alp_set) # randomly selects 3 alphabets from alp_set string
#
#     return user_password + hashed_string
#
#
#
# def save_user(user_input: UserInput):
#     """
#     A function that saves user's info into the EVERY_USER dict and USER_DATABASE list.
#     If user inputs an invalid id, it will raise InvalidUserIDException.
#     It returns the converted User object.
#     """
#
#     if user_input.user_id in EVERY_USER or not user_input.user_id[0].isalpha():
#         raise InvalidUserIDException(user_input.user_id)
#
#     user = User(user_id=user_input.user_id)
#     EVERY_USER[user_input.user_id] = user_input.full_name
#     hashed_password = hash_the_password(user_input.pswd)
#     user_in_db = UserDB(**user_input.dict(), hashed_pswd=hashed_password, stored_date=datetime.now())  # append user's info as an object (db version) into a list: EVERY_USER_DB_VERSION
#     USER_DATABASE.append(user_in_db)
#
#     print("User is successfully saved!")
#
#     return user
#
#
#
# @app.post("/user/", response_model=User, tags=[Tags.user])
# async def create_user(user_input: UserInput):
#     """
#     Calls the save_user function to save user.
#     Returns UserDB object.
#     """
#
#     user_saved = save_user(user_input)
#     return user_saved
#
#
#
#
# @app.get("/user/", tags=[Tags.user])
# async def read_every_user(version: str) -> dict | list | str:
#     """
#     This will return one of these data types (dict, list, str).
#     If the version query is invalid, it will return a string: haha! check your query!
#     Otherwise, it will return a dict or list that includes every user's information.
#     """
#
#     if version == "standard":
#         return read_all(EVERY_USER)
#
#     elif version == "database":
#         return read_all(USER_DATABASE)
#
#     else:
#         return "haha! check your query"
#
#
# def read_all(data):
#     """
#     If something is None (null) it will raise an EmptyException.
#     Otherwise, it will just return something (bad parameter name (something): will change in the future).
#     """
#
#     if not data:
#         raise EmptyException()
#     return data
#
#
#
#
#
#
#
# class SpecificRange:
#
#     """
#     SpecificRange includes 3 queries: q, start, and end.
#     The asterisk exists because the first parameter q's default value is None, which is not allowed in python.
#     """
#
#     def __init__(self, *, q: str | None = None, start: int, end: int):
#
#         self.q = q
#         self.start = start
#         self.end = end
#
#
# @app.get("/readsomedatabase/", tags=[Tags.user])
# async def read_some_database(several: Annotated[SpecificRange, Depends(SpecificRange)]):
#
#     """
#     Using Dependency to read certain amount of data that are stored in the database (list).
#     If q exists, it will be included inside of response dictionary.
#     Otherwise, it will only include several data and this will be determined by start and end queries.
#     It returns a response dictionary.
#     """
#
#     response = {}
#
#     if several.q:
#         response.update({"q": several.q})
#
#     users = USER_DATABASE[several.start: several.end]
#     response.update({"users": users})
#     return response
#
