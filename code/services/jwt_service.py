import datetime
import jwt

from helpers.exceptions import ServerError, Unauthorized

EXPIRATION_DELTA: datetime.timedelta = datetime.timedelta(days=0, hours=0, minutes=15)
ALGORITHM: str = 'HS256'

class JWTService:
    def __init__(self, key:str) -> None:
        self.__key = key

    def create_token(self, user_id: int) -> str:
        payload = {
            'exp': datetime.datetime.utcnow() + EXPIRATION_DELTA,
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
        }
        try:
            return jwt.encode(payload, key=self.__key, algorithm=ALGORITHM)
        except Exception as e:
            raise ServerError() from e

    def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, key=self.__key, algorithms=[ALGORITHM])
            return payload['sub']
        except jwt.ExpiredSignatureError as e:
            raise Unauthorized() from e
        except jwt.InvalidTokenError as e:
            raise Unauthorized() from e
        except Exception as e:
            raise ServerError() from e
