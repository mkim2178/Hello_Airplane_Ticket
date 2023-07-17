from pydantic import BaseModel


class TicketBase(BaseModel):
    destination: str
    seat_level: str
    seat_number: int


class TicketCreate(TicketBase):
    pass


class Ticket(TicketBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    tickets: list[Ticket] = []

    class Config:
        orm_mode = True
