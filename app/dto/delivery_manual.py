import decimal

from app.dto import common as dto_common


class DeliveryManual(dto_common.TGStoreShopEntitiesBaseModel):
    title: str
    description: str | None = None
    contact_phone: str | None = None
    contact_tg_username: str
    price: decimal.Decimal | None = None


class DeliveryManualCreateRequest(dto_common.TGStoreBaseRequest):
    title: str
    description: str | None = None
    contact_phone: str | None = None
    contact_tg_username: str | None = None
    price: decimal.Decimal | None = None


class DeliveryManualUpdateRequest(DeliveryManualCreateRequest):
    title: str | None = None

class DeliveryManualUpdate(dto_common.TGStoreEntityBaseUpdateModel, DeliveryManualUpdateRequest):
    pass
