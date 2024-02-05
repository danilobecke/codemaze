import datetime
from enum import StrEnum, auto
from typing import Any

import jwt

from helpers.config import Config
from helpers.exceptions import ServerError, Unauthorized

ALGORITHM: str = 'HS256'

class JWTService:
    class Intent(StrEnum):
        SESSION = auto()

    def __init__(self, key:str) -> None:
        self.__key = key
        expiration_minutes = int(Config.get('admin.session-duration'))
        self.__expiration_delta = datetime.timedelta(days=0, hours=0, minutes=expiration_minutes)

    def create_token(self, user_id: int, intent: Intent) -> str:
        payload = {
            'exp': datetime.datetime.utcnow() + self.__expiration_delta,
            'iat': datetime.datetime.utcnow(),
            'sub': {
                'intent': intent,
                'user_id': user_id,
            },
        }
        try:
            return jwt.encode(payload, key=self.__key, algorithm=ALGORITHM)
        except Exception as e:
            raise ServerError() from e

    def decode_token(self, token: str, intent: Intent) -> int:
        try:
            payload: dict[str, Any] = jwt.decode(token, key=self.__key, algorithms=[ALGORITHM])
            sub: dict[str, Any] = payload['sub']
            if str(sub['intent']) != intent:
                raise Unauthorized()
            return int(sub['user_id'])
        except jwt.ExpiredSignatureError as e:
            raise Unauthorized() from e
        except jwt.InvalidTokenError as e:
            raise Unauthorized() from e
        except Exception as e:
            raise ServerError() from e
