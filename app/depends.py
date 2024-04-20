from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SQLAlchemySession
from app.db.connection import Session
from app.auth_user import UserUseCases
from app.db.models import UserModel


oauth_scheme = OAuth2PasswordBearer(tokenUrl='/user/login')


def get_db_session():
    try:
        session = Session()
        yield session
    finally:
        session.close()


def token_verifier(
    db_session: SQLAlchemySession = Depends(get_db_session),
    token: str = Depends(oauth_scheme)
) -> UserModel:
    uc = UserUseCases(db_session=db_session)
    return uc.verify_token(access_token=token)
