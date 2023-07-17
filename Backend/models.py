from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, index=True, primary_key=True)
    email = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    full_name = Column(String)
    age = Column(Integer)
    sex = Column(String)

    tickets = relationship("Ticket", back_populates="owner")

    def __repr__(self):
        return f"User Id: {self.id} / User Email: {self.email}"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    departure_destination = Column(String, index=True)
    arrival_destination = Column(String, index=True)
    seat_class = Column(String, index=True)
    seat_number = Column(String, unique=True, index=True)
    departure_date = Column()
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tickets")

    def __repr__(self):
        return f"Ticket Id: {self.id} / " \
               f"Destination: {self.destination} / " \
               f"Seat Level: {self.seat_level} / " \
               f"Seat Number: {self.seat_number} / " \
               f"Owner's ID: {self.owner_id}"
