import datetime
import jwt

from helpers.exceptions import ServerError, Unauthorized

class JWTService:
    __EXPIRATION_DELTA: datetime.timedelta = datetime.timedelta(days=0, hours=0, minutes=15)
    __ALGORITHM: str = 'HS256'
    
    def __init__(self, key:str):
        self.__key = key

    def create_token(self, user_id: int) -> str:
        payload = {
            'exp': datetime.datetime.utcnow() + JWTService.__EXPIRATION_DELTA,
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
        }
        try:
            return jwt.encode(payload, key=self.__key, algorithm=JWTService.__ALGORITHM)
        except Exception:
            raise ServerError()

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, key=self.__key, algorithms=JWTService.__ALGORITHM)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise Unauthorized()
        except jwt.InvalidTokenError:
            raise Unauthorized()
        except Exception:
            raise ServerError()

