import datetime

from sqlalchemy import select, Engine, Sequence
from sqlalchemy.orm import Session
import models, sso
from database import database_engine
from fastapi import HTTPException
from jose import jwt
from jose.constants import ALGORITHMS


class AccountService:
    _database_engine: Engine

    def __init__(self, database_engine: Engine):
        self._database_engine = database_engine

    def get_all(self, limit: int = 10, offset: int = 0) -> Sequence[models.Account]:
        with Session(self._database_engine) as session:
            return session.scalars(select(models.Account).limit(limit).offset(offset)).all()

    def get(self, account_id: int) -> models.Account:
        with Session(self._database_engine) as session:
            account = session.scalar(select(models.Account).where(models.Account.id == account_id))
            if account == None:
                raise HTTPException(status_code=404, detail="User not found")
            return account

    def get_by_name(self, name: str) -> models.Account:
        with Session(self._database_engine) as session:
            return session.scalar(select(models.Account).where(models.Account.name == name))

    def delete(self, account_id: int):
        account = self.get(account_id)
        with Session(self._database_engine) as session:
            session.delete(account)
            session.commit()

    def create(self, name: str):
        account = models.Account(name=name)
        with Session(self._database_engine) as session:
            session.add(account)
            session.commit()
            session.refresh(account)
            return account

    def update(self, account_id: int, name: str):
        account = self.get(account_id)
        account.name = name
        with Session(self._database_engine) as session:
            session.add(account)
            session.commit()
        pass

    def update_last_login(self, account: models.Account):
        account.last_login_date = datetime.datetime.now()

        with Session(self._database_engine) as session:
            session.add(account)
            session.commit()
        pass

    def create_access_token(self, name: str) -> str:
        to_encode = {
            "name": name
        }
        encoded_jwt = jwt.encode(to_encode, sso.google_sso.client_secret.__str__(), algorithm=ALGORITHMS.HS256)
        return encoded_jwt

    def get_by_token(self, session_token: str) -> models.Account:
        if session_token is None:
            return None
        payload = jwt.decode(session_token, sso.google_sso.client_secret.__str__(), algorithms=[ALGORITHMS.HS256])
        username: str = payload.get("name")

        if username is None:
            raise Exception("Token could not be validated")
        return self.get_by_name(username)


accountService = AccountService(database_engine)
