import datetime
import enum
import logging
import typing as t
import uuid

import jwt
from fastapi.security import HTTPBearer

from app import settings

logger = logging.getLogger(__name__)
http_bearer_depends = HTTPBearer()


class TokenType(enum.Enum):
    ACCESS = 'ACCESS'
    REFRESH = 'REFRESH'
    API_KEY = 'API_KEY'


def _generate_jwt_token(payload_data: t.Mapping) -> str:
    new_token = jwt.encode(
        payload=payload_data,
        key=settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return new_token


def decode_token(token: str, aud: t.Iterable[str]):
    """
    :raises jwt.ExpiredSignatureError:
    :raises jwt.InvalidTokenError:
    """
    payload = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        audience=aud,
    )
    return payload


def generate_access_refresh_token(
    user_uuid: uuid.UUID | str,
    username: str,
    role: str | None = 'owner',
    access_token_expiration: float | None = settings.ACCESS_TOKEN_EXPIRATION,
    refresh_token_expiration: float | None = settings.REFRESH_TOKEN_EXPIRATION,
) -> tuple[str, str]:
    current_time = datetime.datetime.now()
    access_expired_time = current_time + datetime.timedelta(minutes=access_token_expiration)
    refresh_expired_time = current_time + datetime.timedelta(minutes=refresh_token_expiration)

    access_token = _generate_jwt_token(
        {
            'jti': str(uuid.uuid4()),
            'aud': 'owner',  # TODO вспомнить че это
            "sub": str(user_uuid),
            "name": username,
            "iat": current_time.timestamp(),
            "exp": access_expired_time.timestamp(),
            "token_type": TokenType.ACCESS.value,
            'role': role
        }
    )

    refresh_token = _generate_jwt_token(
        {
            'jti': str(uuid.uuid4()),
            'aud': 'owner',  # TODO вспомнить че это
            "sub": str(user_uuid),
            "name": username,
            "iat": current_time.timestamp(),
            "exp": refresh_expired_time.timestamp(),
            "token_type": TokenType.REFRESH.value,
            'role': role
        }
    )

    return access_token, refresh_token
