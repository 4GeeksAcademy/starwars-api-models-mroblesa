from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    fav_planets: Mapped[List[FavPlanet]] = relationship("FavPlanet", back_populates="user")
    fav_people: Mapped[List[FavPeople]] = relationship("FavPeople", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name
        }


class Planets(db.Model):
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    gravity: Mapped[int] = mapped_column(Integer, nullable=False)
    image: Mapped[str] = mapped_column(String(120), nullable=True)

    people: Mapped[List[People]] = relationship("People", back_populates="birth_planet")
    fav_planets: Mapped[List[FavPlanet]] = relationship("FavPlanet", back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "population": self.population,
            "gravity": self.gravity,
            "image": self.image
        }


class FavPlanet(db.Model):
    __tablename__ = "favplanet"

    id: Mapped[int] = mapped_column(primary_key=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="fav_planets")
    planet: Mapped[Planets] = relationship("Planets", back_populates="fav_planets")

    def serialize(self):
        return {
            "id": self.id,
            "planet_id": self.planet_id,
            "user_id": self.user_id
        }


class People(db.Model):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(120), nullable=False)
    height: Mapped[str] = mapped_column(String(120), nullable=True)
    image: Mapped[str] = mapped_column(String(120), nullable=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"))

    birth_planet: Mapped[Planets] = relationship(
        "Planets", back_populates="people")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "height": self.height,
            "image": self.image,
            "planet_id": self.planet_id
        }


class FavPeople(db.Model):
    __tablename__ = "favpeople"

    id: Mapped[int] = mapped_column(primary_key=True)
    people_id: Mapped[int] = mapped_column(ForeignKey("people.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped[User] = relationship("User", back_populates="fav_people")
    people: Mapped[People] = relationship("People")

    def serialize(self):
        return {
            "id": self.id,
            "people_id": self.people_id,
            "user_id": self.user_id
        }
