import jwt

import fastapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from app.core import auth as app_auth
from app import settings
from app.db import keys_structure, utils as db_utils, common as db_common
from app.dto import (
    user as dto_user,
)
from app.dto.exceptions import auth as auth_exceptions, shop as shop_exception
from app.handlers import (
    user as user_handlers,
)


security = HTTPBearer()
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

admin_key_header = APIKeyHeader(name="x-admin-key", auto_error=False)
admin_fake_uuid = '00000000-0000-4000-8000-000000000000'


def admin_custom_headers(x_admin_key: str = fastapi.Header()):
    return "hey there"


def check_token_in_blacklist(token_jti: str, table_connection=db_utils.get_tokens_table) -> bool:
    # TODO сходить в базу, посмотрет в черный список, найти запись с jti
    token_item = db_common.get_db_item(
        partkey=keys_structure.token_partkey.format(jti=token_jti),
        sortkey=keys_structure.token_sortkey,
        table_connection=table_connection
    )
    return bool(token_item)


def decode_token(token: str) -> dict:
    try:
        payload = app_auth.decode_token(token=token, aud=['owner'])
        return payload
    except jwt.ExpiredSignatureError:
        raise auth_exceptions.TokenExpired
    except jwt.InvalidTokenError:
        raise auth_exceptions.TokenInvalid


def check_token_payload(payload: dict, token_type: app_auth.TokenType) -> dict:
    payload_token_type = payload.get('token_type')
    if payload_token_type != token_type.value:
        raise auth_exceptions.TokenWrongType(token_type.value)

    token_jti = payload.get('jti', None)
    if token_jti is None:
        raise auth_exceptions.MissedJTI
    elif check_token_in_blacklist(token_jti):
        raise auth_exceptions.TokenBlacklisted

    token_sub = payload.get('sub', None)
    if token_sub is None:
        raise auth_exceptions.MissedSub

    return payload


def parse_token(token: str, token_type: app_auth.TokenType = app_auth.TokenType.ACCESS):
    token_payload = decode_token(token)
    token_payload = check_token_payload(token_payload, token_type)

    return token_payload


def add_token_to_blacklist(token_jti, table_connection=db_utils.get_tokens_table):
    table_connection().put_item(Item={
        "partkey": keys_structure.token_partkey.format(jti=token_jti),
        "sortkey": keys_structure.token_sortkey,
    })


def override_auth_data():
    import uuid
    from app.db import keys_structure as db_keys_structure

    user_uuid = uuid.uuid4()

    user_data = dto_user.User(
        uuid=user_uuid,
        user_uuid=user_uuid,
        tg_id=1,
        tg_first_name="first_name",
        tg_last_name="last_name",
        tg_username="tg_username",
        tg_photo_url='http://www.example.com',
        tg_auth_date=100,
        email='noreply@google.com',
        record_type=db_keys_structure.user_record_type,
    )
    return user_data


# ToDO Refactor this - remove tables from AuthData
def auth_user(credentials: HTTPAuthorizationCredentials = fastapi.Depends(security)) -> dto_user.AuthData:
    # # ToDO Comment on commit!
    # #  Только для тестирования ендпоинтов в локальном режиме, что бы не заморачиваться с авторизацией!
    # if os.getenv("MODE") == "LOCAL_DEV":
    #     return dto_user.AuthData(user=override_auth_data())

    token = credentials.credentials
    token_payload = parse_token(token=token)
    user_uuid = token_payload['sub']
    user_item = user_handlers.handle_get_user_by_id(user_uuid=user_uuid)

    return dto_user.AuthData(user=user_item)


def check_admin_key(api_key: str = fastapi.Security(admin_key_header)):
    if api_key != settings.ADMIN_API_KEY:
        raise auth_exceptions.WrongApiKey
    return True
