import uuid
from pprint import pprint
import typing

import pytest

import pydantic
from pydantic_core.core_schema import uuid_schema
from pydantic_extra_types import color as pydantic_color

import app.dto.common as dto_common
from app.db import keys_structure as db_keys_structure


@pytest.mark.skip
def test_pydantic():

    class TgUser(dto_common.TGStoreEntityBaseModel):
        _partkey: str = db_keys_structure.tg_user_partkey
        _sortkey: str = db_keys_structure.tg_user_sortkey

        id_: int = pydantic.Field(alias='id')
        first_name: str
        last_name: str | None
        username: str
        photo_url: dto_common.StrUrl
        auth_date: int
        user_uuid: dto_common.UUIDasStr
        none_field: str = None

        model_config = pydantic.ConfigDict(
            arbitrary_types_allowed=True,
            extra='allow'
        )

        @pydantic.field_validator('photo_url')
        @classmethod
        def check_photo_url(cls, photo_url):
            return str(photo_url)

    class UpdateTgUser(TgUser):
        model_config = pydantic.ConfigDict(populate_by_name=True)

    tg_user = TgUser(
    id = 1,
    first_name = 'first_name',
    last_name = 'last_name',
    username = 'username',
    auth_date = 100,
    photo_url = 'http://www.example.com',
    tg_hash = 'tg_hash',
    user_uuid = uuid.uuid4(),
    date_create = '2024-09-24T22:20:30.815750',
    uuid = '7dc5ead3-12ef-4422-9b60-8b4fb822fdb0',
    )

    tg_user.aaa = "test"

    pprint(tg_user.model_dump())

    tg_user_update = UpdateTgUser(
    id = 1,
    first_name = 'first_name',
    last_name = 'last_name',
    username = 'username',
    auth_date = 100,
    photo_url = 'http://www.example.com',
    tg_hash = 'tg_hash',
    user_uuid = uuid.uuid4(),
    date_create = '2024-09-24T22:20:30.815750',
    uuid = '7dc5ead3-12ef-4422-9b60-8b4fb822fdb0',
    )

    pprint(tg_user_update.model_dump())


@pytest.mark.skip
def test_pydantic_private_fields():
    PYDANTIC_DB_CONFIG = {"exclude_none": True}
    PYDANTIC_UI_CONFIG = {"exclude_none": True, "exclude": {'partkey', 'sortkey'}, "by_alias": True}

    class TGStoreBaseModel(pydantic.BaseModel):
        _partkey: str | None = None
        _sortkey: str | None = None
        uuid: str

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # Изменяем значение приватных переменных
            self._partkey = kwargs.get('partkey', self._partkey)
            self._sortkey = kwargs.get('sortkey', self._sortkey)

        @property
        def partkey(self):
            return self._partkey

        @property
        def sortkey(self):
            return self._sortkey

        def to_record(self):
            # Создаем словарь с ключами в формате dynamodb для записи в базу:
            # 1. Ключевые слова экранированы "_"
            # 2. partkey и sortkey включены
            data = self.model_dump(**PYDANTIC_DB_CONFIG)
            if hasattr(self, "_partkey"):
                data["partkey"] = self._partkey
            if hasattr(self, "_sortkey"):
                data["sortkey"] = self._sortkey
            return data

        def to_db(self):
            # Создаем словарь с ключами в формате dynamodb:
            # 1. Ключевые слова экранированы "_"
            # 2. partkey и sortkey исключены
            data = self.model_dump(**PYDANTIC_DB_CONFIG, exclude={'partkey', 'sortkey'})
            return data

        def to_ui(self):
            # Создаем словарь с ключами в формате UI для выдачи на фронт, т.е. используются aliasы для fields:
            # 1. Ключевые слова без "_"
            # 2. partkey и sortkey исключены
            data = self.model_dump(**PYDANTIC_UI_CONFIG)
            return data

    class TGStoreEntityBaseModel(TGStoreBaseModel):
        user_uuid: str

    class UserDetails(TGStoreBaseModel):
        first_name: str | None = None

    class User(TGStoreEntityBaseModel, UserDetails):
        tg_id: int

    data = {"partkey": "pk", "sortkey": "sk", "user_uuid": "1", "first_name": "name", "tg_id": 1, "uuid": "UUID"}
    ttt = User(**data)
    print("\n=== model dump:")
    pprint(ttt.model_dump())
    print("\n=== to record:")
    pprint(ttt.to_record())
    print("\n=== to ui:")
    pprint(ttt.to_ui())
    print("\n=== privates only:")
    pprint(ttt.__pydantic_private__)
    print("\n\n\n")

    data2 = {"partkey": "pk", "sortkey": "sk", "uuid": "UUID"}
    ttt2 = TGStoreBaseModel(**data2)
    print("\n=== model dump:")
    pprint(ttt2.model_dump())
    print("\n=== to record:")
    pprint(ttt2.to_record())
    print("\n=== to ui:")
    pprint(ttt2.to_ui())
    print("\n=== privates only:")
    pprint(ttt2.__pydantic_private__)
    print("")

    assert True



@pytest.mark.skip
def test_pydantic_color():
    PYDANTIC_DB_CONFIG = {"exclude_none": True}
    PYDANTIC_UI_CONFIG = {"exclude_none": True, "exclude": {'partkey', 'sortkey'}, "by_alias": True}

    ColorDasStr = typing.Annotated[str | pydantic_color.Color, pydantic.AfterValidator(lambda x: str(x))]

    class TGStoreBaseModel(pydantic.BaseModel):
        uuid: pydantic.UUID4
        str_uuid: pydantic.UUID4
        color: pydantic_color.Color | None = "FFFFFF"
        hex_color: pydantic_color.Color | None = "FFFFFF"

        @pydantic.field_serializer("uuid", "str_uuid", return_type=str, when_used='always')
        @classmethod
        def uuid2str(self, item):
            return str(item)

        @pydantic.field_serializer('hex_color', 'color')
        @classmethod
        def colors(self, hex_color):
            return str(hex_color)

        def to_record(self):
            # Создаем словарь с ключами в формате dynamodb для записи в базу:
            # 1. Ключевые слова экранированы "_"
            # 2. partkey и sortkey включены
            data = self.model_dump(**PYDANTIC_DB_CONFIG)
            if hasattr(self, "_partkey"):
                data["partkey"] = self._partkey
            if hasattr(self, "_sortkey"):
                data["sortkey"] = self._sortkey
            return data

        def to_db(self):
            # Создаем словарь с ключами в формате dynamodb:
            # 1. Ключевые слова экранированы "_"
            # 2. partkey и sortkey исключены
            data = self.model_dump(**PYDANTIC_DB_CONFIG, exclude={'partkey', 'sortkey'})
            return data

        def to_ui(self):
            # Создаем словарь с ключами в формате UI для выдачи на фронт, т.е. используются aliasы для fields:
            # 1. Ключевые слова без "_"
            # 2. partkey и sortkey исключены
            data = self.model_dump(**PYDANTIC_UI_CONFIG)
            return data

    data = {"uuid": str(uuid.uuid4()), "color": pydantic_color.Color("white"), "str_uuid": uuid.uuid4(), "hex_color": "#FFFFFF"}
    ttt = TGStoreBaseModel(**data)
    print("\n=== model dump:")
    pprint(ttt.model_dump())
    print("\n=== to record:")
    pprint(ttt.to_record())
    print("\n=== to ui:")
    pprint(ttt.to_ui())
    print("\n=== privates only:")
    pprint(ttt.__pydantic_private__)
    print("\n\n\n")

    assert True
