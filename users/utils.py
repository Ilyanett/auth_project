import jwt
import datetime
from django.conf import settings


def generate_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(
            hours=settings.JWT_EXPIRATION_HOURS
        ),
        'iat': datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )
    return payload
