from sqlalchemy.orm import Session

import models, schemas

import hashlib, random, string


EVERY_ALPHABET = string.ascii_lowercase


# read user
def get_user(db: Session, user_id: int):
    """
    This function returns models.User object to read the user by id.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


# read user by email
def get_user_by_email(db: Session, email: str):
    """
    This function returns models.User object to read the user by email.
    """
    return db.query(models.User).filter(models.User.email == email).first()


# read a certain amount of users
def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    This function returns models.User objects to read certain amount of users.
    """
    return db.query(models.User).offset(skip).limit(limit).all()


# create user
def create_user(db: Session, user: schemas.UserCreate):
    """
    This function generates a random string (length is 10 and this will be stored as a hashed function (for practice)
    and creates a new models.User object.
    """
    # hashed_password = user.password + "_" + str(hashlib.blake2s(user.password.encode()).hexdigest())[:10]  # used blake2s to get a hashed password
    hashed_password = random_string_generator(10)  # version 2 (generate a random string with length 10)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# create a random string (length: 10)
def random_string_generator(str_len):
    """
    This function will be used from create_user function to generate a random string (length is 10).
    """
    random_string = ""
    for i in range(str_len):
        random_string += EVERY_ALPHABET[random.randint(0, 25)]
    return random_string


# delete user
def delete_user(db: Session, user_id: int):
    """
    This function will delete a user from the database (it requires user's id).
    It calls get_every_ticket_by_id function and delete_every_tickets function.
    If user has at least 1 ticket, it will delete every ticket before delete the user.
    """

    if get_every_ticket_by_id(db, user_id):
        print(delete_every_tickets(db, user_id))

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(db_user)
    db.commit()
    return f"user_id={user_id} has been deleted from the database!"


# read tickets
def get_tickets(db: Session, skip: int = 0, limit: int = 100):
    """
    This function returns models.Ticket objects to read certain amount of tickets.
    """
    return db.query(models.Ticket).offset(skip).limit(limit).all()


# create a ticket
def create_user_ticket(db: Session, ticket: schemas.TicketCreate, user_id: int):
    """
    This function creates a models.Ticket object.
    """
    db_ticket = models.Ticket(**ticket.dict(), owner_id=user_id)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


# read a 1 ticket by id
def get_ticket_by_id(db: Session, user_id: int, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.owner_id == user_id).filter(models.Ticket.id == ticket_id).first()


# read certain user's every ticket
def get_every_ticket_by_id(db: Session, user_id: int):
    return db.query(models.Ticket).filter(models.Ticket.owner_id == user_id).all()


# delete certain user's ticket
def delete_ticket(db: Session, user_id: int, ticket_id: int):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.owner_id == user_id).filter(models.Ticket.id == ticket_id).first()
    db.delete(db_ticket)
    db.commit()
    return f"user_id={user_id} -> ticket_id={ticket_id} has been deleted from the database!"


# delete certain user's every ticket
def delete_every_tickets(db: Session, user_id: int):
    db_every_tickets_by_id = db.query(models.Ticket).filter(models.Ticket.owner_id == user_id).all()

    for ticket in db_every_tickets_by_id:
        delete_ticket(db, user_id, ticket_id=ticket.id)

    return f"user_id={user_id} tickets are all deleted!"
