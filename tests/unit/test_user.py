import pytest
from unittest.mock import patch
import fastapi

from app.handlers import (
    user as user_handlers
)
from app.dto import (
    user as user_dto
)
from app.dto.exceptions import auth as auth_exceptions
from app.core import auth as app_auth
from app.db import common as db_common, keys_structure as db_keys_structure, utils as db_utils


def test_login_when_new_user(request, tables_connection):
    tg_id = 1
    first_name = 'first_name'
    last_name = 'last_name'
    username = 'username'
    auth_date = 100
    photo_url = 'http://www.example.com'
    tg_hash = 'tg_hash'

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': tg_user_db["partkey"],
            'sortkey': tg_user_db["sortkey"]
        })

    request.addfinalizer(resource_teardown)

    with patch('app.handlers.user.assert_tg_data') as tg_mock:
        result = user_handlers.handle_login_user(
            tg_id, first_name, last_name, username, auth_date, photo_url, tg_hash
        )
        tg_user_db = db_common.get_db_item(
            partkey=db_keys_structure.tg_user_partkey,
            sortkey=db_keys_structure.tg_user_sortkey.format(tg_id=tg_id)
        )
        user_db = db_common.get_db_item(
            partkey=db_keys_structure.user_partkey,
            sortkey=db_keys_structure.user_sortkey.format(uuid=tg_user_db['user_uuid'])
        )


        assert len(tables_connection.general_table.scan()['Items']) == 2
        assert tg_user_db['user_uuid'] == user_db['user_uuid']
        assert tg_user_db['user_uuid'] == user_db['uuid_']
        assert tg_user_db['id_'] == user_db['tg_id']


def test_login_when_user_exist(insert_user, request):
    user_tg_item, user_item = insert_user
    tg_hash = 'tg_hash'

    # юзер уже есть в базе
    # при логине синхронизируются данные из телеги: если новое имя - оно обновится
    new_lastname = 'new_lastname'

    with patch('app.handlers.user.assert_tg_data') as tg_mock:
        result = user_handlers.handle_login_user(
            tg_id=user_tg_item.id_,
            first_name=user_tg_item.first_name,
            last_name=new_lastname,
            username=user_tg_item.username,
            auth_date=user_tg_item.auth_date,
            photo_url=user_tg_item.photo_url,
            tg_hash=tg_hash,
        )
        db_items = db_utils.get_gen_table().scan()['Items']

        assert len(db_items) == 2
        db_user_item = [item for item in db_items if item['partkey'] == 'user_'][0]
        db_tg_user_item = [item for item in db_items if item['partkey'] == 'tg_user'][0]

        assert db_tg_user_item['last_name'] == new_lastname
        assert db_user_item['tg_last_name'] == new_lastname
        assert db_tg_user_item['user_uuid'] == db_user_item['user_uuid']
        assert db_tg_user_item['user_uuid'] == db_user_item['uuid_']
        assert db_tg_user_item['id_'] == db_user_item['tg_id']
        assert db_user_item['email'] == 'noreply@google.com'


def test_tokens(insert_user, request):
    user_tg_item, user_item = insert_user

    access_token, refresh_token = app_auth.generate_access_refresh_token(
        user_uuid=user_item.uuid_,
        username=user_tg_item.username,
    )

    # обновим токен
    new_tokens = user_handlers.handle_refresh_token(token=refresh_token)
    assert new_tokens.access_token != access_token
    assert new_tokens.refresh_token != refresh_token

    assert len(db_utils.get_tokens_table().scan()['Items']) == 1

    # обновим еще раз со старым токеном, должна быть ошибка
    with pytest.raises(fastapi.HTTPException) as exc_info:
        new_tokens = user_handlers.handle_refresh_token(token=refresh_token)
        assert exc_info == auth_exceptions.TokenBlacklisted

    # а теперь логаут с обновленным токеном
    user_handlers.handle_logout(token=new_tokens.refresh_token)
    assert len(db_utils.get_tokens_table().scan()['Items']) == 2


def test_update_details(insert_user, request):
    user_tg_item, user_item = insert_user

    user_details = user_dto.UserDetails(
        first_name='Имя', last_name='Фамилия', patronymic=None
    )

    result = user_handlers.handle_update_details(
        user=user_item,
        details=user_details,
    )

    assert result.first_name == user_details.first_name
    assert result.last_name == user_details.last_name
    assert result.patronymic == user_details.patronymic
    assert result.email == 'noreply@google.com'
    assert result._partkey == user_item._partkey
    assert result._sortkey == user_item._sortkey
    assert result.uuid_ == user_item.uuid_
