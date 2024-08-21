import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, BigInteger, ARRAY
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    age = Column(BigInteger)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    longitude = Column(String, nullable=False)
    latitude = Column(String, nullable=False)
    bio = Column(String)

    interests = Column(ARRAY(String))
    gender = Column(String)

    travels = relationship("Travel", secondary="user_travels", back_populates="participants")


class Travel(Base):
    __tablename__ = "travels"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    description = Column(String)

    creator_id = Column(BigInteger, ForeignKey("users.id"))

    locations = relationship("Location", order_by="Location.start_date, Location.end_date", back_populates="travel")
    notes = relationship("Note", back_populates="travel")
    participants = relationship("User", secondary="user_travels", back_populates="travels")


class UserTravel(Base):
    __tablename__ = "user_travels"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    travel_id = Column(String, ForeignKey("travels.id"), primary_key=True)


class Location(Base):
    __tablename__ = "locations"

    id = Column(BigInteger, primary_key=True, index=True)
    travel_id = Column(String, ForeignKey("travels.id"))

    country = Column(String)
    city = Column(String)

    longitude = Column(String)
    latitude = Column(String)

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    travel = relationship("Travel", back_populates="locations")


class Note(Base):
    __tablename__ = "notes"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)

    file_type = Column(String)
    file_id = Column(String)

    travel_id = Column(String, ForeignKey("travels.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))

    is_private = Column(Boolean, default=False)

    travel = relationship("Travel", back_populates="notes")
