import datetime

import pydantic
import enum

from app.dto import common as dto_common
from app.db import keys_structure as db_keys_structure


class ShopTypes(str, enum.Enum):
    online_store = "OnlineStore"
    information_site = "InformationSite"


class Shop(dto_common.TGStoreOwnerBaseModel):
    model_config = pydantic.ConfigDict(use_enum_values=True, populate_by_name=True)

    title: str
    description: str | None = None
    subscription_active: bool | None = False
    subscription_expire_at: dto_common.StrDate | None = datetime.datetime.now().isoformat()
    template_uuid: dto_common.UUIDasStr = None
    shop_type: ShopTypes
    logo_url: dto_common.StrUrl

    @pydantic.field_validator('subscription_expire_at')
    @classmethod
    def check_subscription_expire_at(cls, subscription_expire_at):
        if subscription_expire_at:
            return subscription_expire_at.isoformat()
        else:
            return subscription_expire_at


class CreateShopRequest(dto_common.TGStoreBaseRequest):
    title: str
    description: str | None = None
    shop_type: ShopTypes


class ShopUpdateRequest(dto_common.TGStoreBaseRequest):
    title: str | None = None
    description: str | None = None
    shop_type: ShopTypes | None = None
    template_uuid: dto_common.UUIDasStr | None = None


class ShopUpdate(dto_common.TGStoreEntityBaseUpdateModel, ShopUpdateRequest):
    logo_url: dto_common.StrUrl | None = None
    inactive: bool | None = None


class ShopUpdateSubscription(dto_common.TGStoreBaseRequest, dto_common.TGStoreBaseModel):
    subscription_active: bool | None = None
    subscription_expire_at: datetime.datetime | None = None
