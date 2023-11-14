import datetime
from typing import Any

import jwt

from helpers.config import Config
from helpers.exceptions import ServerError, Unauthorized

ALGORITHM: str = 'HS256'

class JWTService:
    def __init__(self, key:str) -> None:
        self.__key = key
        expiration_minutes = int(Config.get('admin.session-duration'))
        self.__expiration_delta = datetime.timedelta(days=0, hours=0, minutes=expiration_minutes)

    def create_token(self, user_id: int) -> str:
        payload = {
            'exp': datetime.datetime.utcnow() + self.__expiration_delta,
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
        }
        try:
            return jwt.encode(payload, key=self.__key, algorithm=ALGORITHM)
        except Exception as e:
            raise ServerError() from e

    def decode_token(self, token: str) -> int:
        try:
            payload: dict[str, Any] = jwt.decode(token, key=self.__key, algorithms=[ALGORITHM])
            return int(payload['sub'])
        except jwt.ExpiredSignatureError as e:
            raise Unauthorized() from e
        except jwt.InvalidTokenError as e:
            raise Unauthorized() from e
        except Exception as e:
            raise ServerError() from e
