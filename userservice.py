import datetime

from sqlalchemy import select, Engine, Sequence
from sqlalchemy.orm import Session
import models, sso
from database import database_engine
from fastapi import HTTPException
from jose import jwt
from jose.constants import ALGORITHMS


class UserService:
    _database_engine: Engine

    def __init__(self, database_engine: Engine):
        self._database_engine = database_engine

    def get_all(self, limit: int = 10, offset: int = 0) -> Sequence[models.Account]:
        with Session(self._database_engine) as session:
            return session.scalars(select(models.Account).limit(limit).offset(offset)).all()

    def get(self, user_id: int) -> models.Account:
        with Session(self._database_engine) as session:
            user = session.scalar(select(models.Account).where(models.Account.id == user_id))
            if user == None:
                raise HTTPException(status_code=404, detail="User not found")
            return user

    def get_by_name(self, name: str) -> models.Account:
        with Session(self._database_engine) as session:
            return session.scalar(select(models.Account).where(models.Account.name == name))

    def delete(self, user_id: int):
        user = self.get(user_id)
        with Session(self._database_engine) as session:
            session.delete(user)
            session.commit()

    def create(self, name: str):
        user = models.Account(name=name)
        with Session(self._database_engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def update(self, user_id: int, name: str):
        user = self.get(user_id)
        user.name = name
        with Session(self._database_engine) as session:
            session.add(user)
            session.commit()
        pass

    def update_last_login(self, user: models.Account):
        user.last_login_date = datetime.datetime.now()

        with Session(self._database_engine) as session:
            session.add(user)
            session.commit()
        pass

    def create_access_token(self, name: str) -> str:
        to_encode = {
            "username": name
        }
        encoded_jwt = jwt.encode(to_encode, sso.google_sso.client_secret.__str__(), algorithm=ALGORITHMS.HS256)
        return encoded_jwt

    def get_by_token(self, session_token: str) -> models.Account:
        if session_token is None:
            return None
        payload = jwt.decode(session_token, sso.google_sso.client_secret.__str__(), algorithms=[ALGORITHMS.HS256])
        username: str = payload.get("username")

        if username is None:
            raise Exception("Token could not be validated")
        return self.get_by_name(payload.get("username"))


userService = UserService(database_engine)
