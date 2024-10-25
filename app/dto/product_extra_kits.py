import decimal

from app.dto import common as dto_common


class ProductExtraKit(dto_common.TGStoreShopProductsBaseModel):
    title: str
    price: decimal.Decimal
    addons: list[str]


class ProductExtraKitCreateRequest(dto_common.TGStoreBaseRequest):
    title: str
    price: float
    addons: list[str]


class ProductExtraKitUpdateRequest(dto_common.TGStoreBaseRequest):
    title: str | None = None
    price: float | None = None
    addons: list[str] | None = None

class ProductExtraKitUpdate(dto_common.TGStoreEntityBaseUpdateModel, ProductExtraKitUpdateRequest):
    price: decimal.Decimal | None = None
