import uuid
import typing
import datetime
import json

import pydantic
from pydantic_extra_types import color as pydantic_color

from pydantic.functional_serializers import PlainSerializer


UUIDasStr = typing.Annotated[pydantic.UUID4, PlainSerializer(lambda x: str(x), return_type=str)]
StrUrl = typing.Annotated[pydantic.HttpUrl, PlainSerializer(lambda x: str(x), return_type=str)]
StrColor = typing.Annotated[pydantic_color.Color, PlainSerializer(lambda x: str(x), return_type=str)]
StrDate =  typing.Annotated[datetime.datetime, PlainSerializer(lambda x: str(x), return_type=str)]
StrTime = typing.Annotated[datetime.time, PlainSerializer(lambda x: str(x), return_type=str)]

PYDANTIC_UI_CONFIG = {"exclude_none": True, "exclude": {'partkey', 'sortkey'}, "by_alias": True}
PYDANTIC_DB_CONFIG = {"exclude_none": True}


class SystemFields(pydantic.BaseModel):
    uuid_: UUIDasStr = pydantic.Field(..., alias='uuid')
    created_at: int | None = None
    updated_at: int | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PaginationInfo(pydantic.BaseModel):
    current_page: int
    on_page: int
    total_pages: int
    total_count: int


class TGStoreBaseModel(pydantic.BaseModel):
    _partkey: str | None = None
    _sortkey: str | None = None
    _record_type: str | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Изменяем значение приватных переменных
        self._partkey = kwargs.get('partkey', self._partkey)
        self._sortkey = kwargs.get('sortkey', self._sortkey)
        self._record_type = kwargs.get('record_type', self._record_type)

    @property
    def partkey(self):
        return self._partkey

    @property
    def sortkey(self):
        return self._sortkey

    @property
    def record_type(self):
        return self._record_type

    def to_record(self):
        # Создаем словарь с ключами в формате dynamodb для записи в базу:
        # 1. Ключевые слова экранированы "_"
        # 2. partkey и sortkey включены
        data = self.model_dump(**PYDANTIC_DB_CONFIG)
        if hasattr(self, "_partkey"):
            data["partkey"] = self._partkey
        if hasattr(self, "_sortkey"):
            data["sortkey"] = self._sortkey
        if hasattr(self, "_record_type") and self._record_type:
            data["record_type"] = self._record_type
            return data
        return data

    def to_db(self):
        # Создаем словарь с ключами в формате dynamodb:
        # 1. Ключевые слова экранированы "_"
        # 2. partkey и sortkey исключены
        data = self.model_dump(**PYDANTIC_DB_CONFIG, exclude={'partkey', 'sortkey'})
        if hasattr(self, "_record_type") and self._record_type:
            data["record_type"] = self._record_type
        return data

    def to_ui(self):
        # Создаем словарь с ключами в формате UI для выдачи на фронт, т.е. используются aliasы для fields:
        # 1. Ключевые слова без "_"
        # 2. partkey и sortkey исключены
        data = self.model_dump(**PYDANTIC_UI_CONFIG)
        return data


class TGStoreEntityBaseUpdateModel(TGStoreBaseModel):
    user_uuid: pydantic.UUID4 # ID пользователя создавшего запись.
    date_create: datetime.datetime = None # Дата создания записи
    date_update: datetime.datetime = datetime.datetime.now().isoformat() # Дата обновления записи
    inactive: bool | None = False # Активна запись или нет. Удаленные записи мы не удаляем, а делаем неактивными!

    @pydantic.field_validator('date_create', mode="after")
    @classmethod
    def update_date_create(cls, date_create):
        if date_create:
            return date_create.isoformat()
        else:
            return date_create

    @pydantic.field_validator('date_update', mode="after")
    @classmethod
    def update_date_update(cls, date_update):
        return datetime.datetime.now().isoformat()

    @pydantic.field_serializer("user_uuid", return_type=str, when_used='always')
    @classmethod
    def user_uuid_to_str(self, item):
        if item:
            return str(item)
        else:
            return item


class TGStoreEntityBaseModel(TGStoreEntityBaseUpdateModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    uuid_: pydantic.UUID4 = pydantic.Field(str(uuid.uuid4()), alias="uuid") # ID записи

    @pydantic.field_serializer("uuid_", return_type=str, when_used='always')
    @classmethod
    def uuid_to_str(self, item):
        if item:
            return str(item)
        else:
            return item


class TGStoreOwnerBaseModel(TGStoreEntityBaseModel):
    owner_uuid: pydantic.UUID4 # ID владельца магазина

    @pydantic.field_serializer("owner_uuid", return_type=str, when_used='always')
    @classmethod
    def owner_uuid_to_str(self, item):
        if item:
            return str(item)
        else:
            return item


class TGStoreShopEntitiesBaseModel(TGStoreOwnerBaseModel):
    shop_uuid: pydantic.UUID4 # ID магазина

    @pydantic.field_serializer("shop_uuid", return_type=str, when_used='always')
    @classmethod
    def shop_uuid_to_str(self, item):
        if item:
            return str(item)
        else:
            return item


class TGStoreShopProductsBaseModel(TGStoreShopEntitiesBaseModel):
    product_uuid: pydantic.UUID4 # ID товара

    @pydantic.field_serializer("product_uuid", return_type=str, when_used='always')
    @classmethod
    def product_uuid_to_str(self, item):
        if item:
            return str(item)
        else:
            return item


class TGStoreBaseRequest(pydantic.BaseModel):

    @pydantic.model_validator(mode='before')
    @classmethod
    def validate_from_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class TGStoreBaseDeleteModel(TGStoreBaseModel):
    user_uuid: pydantic.UUID4 # ID пользователя создавшего запись.
    date_update: datetime.datetime = datetime.datetime.now().isoformat()
    inactive: bool = True

    @pydantic.field_serializer("user_uuid", return_type=str, when_used='always')
    @classmethod
    def user_uuid_to_str(self, item):
        if item:
            return str(item)
        else:
            return item

    @pydantic.field_serializer('date_update', return_type=str, when_used='always')
    @classmethod
    def update_date_update(cls, date_update):
        return datetime.datetime.now().isoformat()

class ResponseNoBody(pydantic.BaseModel):
    message: str = "Operation Successful"