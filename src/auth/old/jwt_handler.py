import time

from jose import jwt

from config import JWT_ACCESS_SECRET_KEY

JWT_SECRET_KEY = JWT_ACCESS_SECRET_KEY
JWT_ALGORITHM = 'HS256'


def token_response(token: str):
    return {
        'access_tocker': token
    }


def sign_jwt(user_id: str):
    payload = {
        'user_id': user_id,
        'expire': time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decode_jwt(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decode_token if decode_token.get('expires') >= time.time() else None
    except:
        return {}
