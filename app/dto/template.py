import pydantic

from app.dto import common as dto_common
from app.db import keys_structure as db_keys_structure
from app.handlers import auth as auth_handlers

class Template(dto_common.TGStoreEntityBaseModel):
    _partkey: str = db_keys_structure.template_partkey
    _sortkey: str = db_keys_structure.template_sortkey

    title: str
    description: str | None = None
    photo_url: dto_common.StrUrl
    template_url: dto_common.StrUrl
    exclusive_owner_uuid: dto_common.UUIDasStr | None = None
    user_uuid: pydantic.UUID4 = auth_handlers.admin_fake_uuid


class TemplateRequestBody(dto_common.TGStoreBaseModel, dto_common.TGStoreBaseRequest):
    title: str
    description: str | None = None
    template_url: dto_common.StrUrl
    exclusive_owner_uuid: dto_common.UUIDasStr | None = None


class TemplateUpdateBody(TemplateRequestBody):
    title: str | None = None
    template_url: dto_common.StrUrl | None = None
