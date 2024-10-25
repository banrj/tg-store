import datetime
import hashlib
import hmac
import uuid
import logging
import os

import pydantic

from app import settings
from app.core import auth as app_auth
from app.handlers import (
    auth as auth_handlers,
)
from app.db import keys_structure as db_keys_structure, utils as db_utils, common as db_common
from app.dto import (
    user as user_dto,
    auth as auth_dto
)
from app.dto.exceptions import user as user_exceptions
from app.dto import common as dto_common


logger = logging.getLogger(__name__)


def check_string(
    id_: int,
    first_name: str,
    last_name: str,
    username: str,
    photo_url: dto_common.StrUrl,
    auth_date: int,
):
    return f"auth_date={int(auth_date)}\nfirst_name={first_name}\nid={id_}\nlast_name={last_name}\nphoto_url={photo_url}\nusername={username}"


def assert_tg_data(
    tg_id: int,
    first_name: str,
    last_name: str | None,
    username: str,
    auth_date: int,
    photo_url: dto_common.StrUrl,
    tg_hash: str,
):
    try:
        signature = hmac.new(
            key=bytes.fromhex(settings.TG_SHA256_HASH_BOT_TOKEN),
            msg=check_string(
                tg_id, first_name, last_name, username, photo_url, auth_date
            ).encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        if os.getenv("MODE") not in [
            "LOCAL_DEV",
            "CICD",
        ]:  # если режим локальной разработки или сисд, то не проверять хеш
            assert signature == tg_hash  # TODO
    except AssertionError:
        raise user_exceptions.InvalidTGAuthData


def get_tg_user_by_id(tg_id) -> user_dto.TgUser | None:
    db_item = db_common.get_db_item(
        partkey=db_keys_structure.tg_user_partkey,
        sortkey=db_keys_structure.tg_user_sortkey.format(tg_id=tg_id),
    )

    return user_dto.TgUser(**db_item) if bool(db_item) else None


def get_user_by_id(user_uuid) -> user_dto.User | None:
    db_item = db_common.get_db_item(
        partkey=db_keys_structure.user_partkey,
        sortkey=db_keys_structure.user_sortkey.format(uuid=user_uuid),
    )
    return user_dto.User(**db_item) if db_item else None


# =======================================


def handle_login_user(
    tg_id: int,
    first_name: str,
    last_name: str | None,
    username: str,
    auth_date: int,
    photo_url: dto_common.StrUrl,
    tg_hash: str,
) -> auth_dto.TokenPair:
    assert_tg_data(
        tg_id, first_name, last_name, username, auth_date, photo_url, tg_hash
    )

    # перезаписываем данные TG пользователя свежими
    tg_user_db = get_tg_user_by_id(tg_id=tg_id)
    tg_user_payload = user_dto.TgUser(
        id_=tg_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        photo_url=photo_url,
        auth_date=auth_date,
        user_uuid=tg_user_db.user_uuid if tg_user_db else uuid.uuid4(),
        date_create=tg_user_db.date_create if tg_user_db else datetime.datetime.now(),
        record_type=db_keys_structure.tg_user_record_type
    )
    tg_user_payload._parekey = db_keys_structure.tg_user_partkey
    tg_user_payload._sortkey = db_keys_structure.tg_user_sortkey.format(tg_id=tg_id)
    db_utils.get_gen_table().put_item(Item=tg_user_payload.to_record())

    # обновляем данные TG пользователя в записи TG Store пользователя
    user_payload = user_dto.User(
        uuid_=tg_user_payload.user_uuid,
        user_uuid=tg_user_payload.user_uuid,
        tg_id=tg_user_payload.id_,
        tg_first_name=tg_user_payload.first_name,
        tg_last_name=tg_user_payload.last_name,
        tg_username=tg_user_payload.username,
        tg_photo_url=tg_user_payload.photo_url,
        tg_auth_date=tg_user_payload.auth_date,
        date_create=tg_user_payload.date_create,
        record_type=db_keys_structure.user_record_type
    )
    user_payload._partkey = db_keys_structure.user_partkey
    user_payload._sortkey = db_keys_structure.user_sortkey.format(uuid=tg_user_payload.user_uuid)
    db_utils.get_gen_table().update_item(**db_common.pydantic_db_update_helper(user_payload))

    access_token, refresh_token = app_auth.generate_access_refresh_token(
        user_payload.uuid_, user_payload.tg_username
    )

    return auth_dto.TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


def handle_refresh_token(token: str) -> auth_dto.TokenPair:
    token_payload = auth_handlers.parse_token(
        token=token,
        token_type=app_auth.TokenType.REFRESH,
    )
    token_jti = token_payload["jti"]
    auth_handlers.add_token_to_blacklist(token_jti=token_jti)

    access_token, refresh_token = app_auth.generate_access_refresh_token(
        user_uuid=token_payload["sub"],
        username=token_payload["name"],
    )

    return auth_dto.TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


def handle_logout(token: str) -> None:
    token_payload = auth_handlers.parse_token(
        token=token,
        token_type=app_auth.TokenType.REFRESH,
    )
    token_jti = token_payload["jti"]
    auth_handlers.add_token_to_blacklist(token_jti=token_jti)


def handle_get_user(user_uuid: dto_common.UUIDasStr) -> user_dto.User:
    item = get_user_by_id(user_uuid=user_uuid)

    if item is None:
        raise user_exceptions.UserNotFound

    return item


def handle_get_user_by_id(user_uuid: dto_common.UUIDasStr) -> user_dto.User:
    item = get_user_by_id(user_uuid=user_uuid)

    if item is None:
        raise user_exceptions.UserNotFound

    return item


def handle_update_details(user: user_dto.User, details: user_dto.UserDetails) -> user_dto.User:
    details._partkey = db_keys_structure.user_partkey
    details._sortkey = db_keys_structure.user_sortkey.format(uuid=user.uuid_)

    updated_user = db_common.update_db_record(db_common.pydantic_db_update_helper(details))

    return user_dto.User(**updated_user)
