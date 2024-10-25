import datetime
import pydantic

from app import settings
import app.dto.common as dto_common
from app.db import utils as db_utils, keys_structure as db_keys_structure

# TG auth response
# {
#     "user": {
#         "id": 414120922,
#         "first_name": "Dmitrii",
#         "last_name": "Popov",
#         "username": "dympopov",
#         "photo_url": "https:\/\/t.me\/i\/userpic\/320\/rf9hgIJ_XHG3sQOaD4YwTsM9oM6vtNwTiCx-6a7JSwU.jpg",
#         "auth_date": 1727100725,
#         "hash": "921bac283027ec2b0e880653023d439e89103cddc01834df1f2dc762865b070c"
#     },
#     "html": "<button class=\"btn tgme_widget_login_button\" onclick=\"return TWidgetLogin.auth();\"><i class=\"tgme_widget_login_button_icon\"><\/i>Log in as <span dir=\"auto\">Dmitrii<\/span><\/button><i class=\"tgme_widget_login_user_photo bgcolor5\" data-content=\"D\" onclick=\"return TWidgetLogin.auth();\"><img src=\"https:\/\/cdn4.telesco.pe\/file\/GhUvDyvP6v45wv0KK1y7xv321xwKaSUTvavFP9mMPs9q6gh8NK6i1J2xntNvkMXwI37LXiNP9HYYtk0l7ag4K-1jz2msSguaVOzqYVYt1KJuXoqF2mvoxhAzedBAMxL9WIsMs7A-AvK6KeTzdFP8LSng1xxe7wL3gLpKiP-YB4HgpBL_Y30aI5FoO8vT_1Hnmy0lbyHC3kqLSlJWHM1xbX4IAVTgEkDhnEMvncG2oFaYjOlC1y1Yd_6oX5LCnSfXlq_j7kBs-zJc0farVPgdhNtd0zDYbGL1UfySw7e3ozoShYv_iDXevFbK3paFLpPUyesrwRdR1lXu-J1bllBfVw.jpg\"><\/i>",
#     "origin": "https:\/\/tg-store-mvp-front-admin.website.yandexcloud.net"
# }
class TelegramAuthorizationData(pydantic.BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    photo_url: str
    auth_date: int
    hash: str = pydantic.Field(..., max_length=64, min_length=64)

    @pydantic.field_validator("auth_date", mode="before")
    @classmethod
    def validate_auth_date(cls, v) -> int:
        minute_ago_datetime = datetime.datetime.now() - datetime.timedelta(minutes=settings.MIN_TG_AUTH_DATETIME)
        if datetime.datetime.fromtimestamp(v) < minute_ago_datetime:
            raise ValueError('Auth datetime is expired!')
        return v


class TgUser(dto_common.TGStoreEntityBaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    _partkey: str = db_keys_structure.tg_user_partkey
    _sortkey: str = db_keys_structure.tg_user_sortkey

    id_: int = pydantic.Field(alias='id')
    first_name: str
    last_name: str | None
    username: str
    photo_url: dto_common.StrUrl
    auth_date: int


class UserDetails(dto_common.TGStoreBaseModel):
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    birthdate: datetime.datetime | None = None

    phone: str | None = pydantic.Field(
        default=None, pattern=r'^(8|\+7)\d{10}$', examples=['88005553535', '+78005553535']
    )
    email: pydantic.EmailStr | None = None

    passport_seria: int | None = pydantic.Field(default=None, ge=1000, le=9999)
    passport_number: int | None = pydantic.Field(default=None, ge=100000, le=999999)
    passport_issued_by: str | None = None
    passport_issued_date: int | None = None
    passport_org_name: str | None = None
    passport_org_code: str | None = pydantic.Field(default=None, pattern=r'^\d{3}-\d{3}$', examples=['123-456'])

    @pydantic.field_validator('birthdate', mode="after")
    @classmethod
    def update_birthdate(cls, birthdate):
        if birthdate:
            return birthdate.isoformat()
        else:
            return birthdate


class User(dto_common.TGStoreEntityBaseModel, UserDetails):
    tg_id: int
    tg_first_name: str
    tg_last_name: str | None
    tg_username: str
    tg_photo_url: dto_common.StrUrl
    tg_auth_date: int


class AuthData(pydantic.BaseModel):
    user: User

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)


class Names(pydantic.BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None


class Phone(pydantic.BaseModel):
    phone: str | None = pydantic.Field(
        default=None, pattern=r'^(8|\+7)\d{10}$', examples=['88005553535', '+78005553535']
    )


class Passport(pydantic.BaseModel):
    passport_seria: int | None = pydantic.Field(default=None, ge=1000, le=9999)
    passport_number: int | None = pydantic.Field(default=None, ge=100000, le=999999)
    passport_issued_by: str | None = None
    passport_issued_date: int | None = None
    passport_org_name: str | None = None
    passport_org_code: str | None = pydantic.Field(default=None, pattern=r'^\d{3}-\d{3}$', examples=['123-456'])
