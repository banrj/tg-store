import decimal

from app.dto import common as dto_common


class ProductBaseInfo(dto_common.TGStoreShopProductsBaseModel):
    title: str
    description: str
    category_uuids: list[dto_common.UUIDasStr]
    image_url: dto_common.StrUrl
    price: decimal.Decimal | None = None


class ProductBaseInfoCreateRequest(dto_common.TGStoreBaseRequest):
    title: str
    description: str
    category_uuids: list[dto_common.UUIDasStr]


class ProductBaseInfoUpdateRequest(ProductBaseInfoCreateRequest):
    title: str | None = None
    description: str | None = None
    category_uuids: list[dto_common.UUIDasStr] | None = None
    inactive: bool | None = None


class ProductBaseInfoUpdate(dto_common.TGStoreEntityBaseUpdateModel, ProductBaseInfoUpdateRequest):
    image_url: dto_common.StrUrl | None = None


class ProductBaseInfoUpdateMinimalPrice(dto_common.TGStoreEntityBaseUpdateModel):
    price: decimal.Decimal | None = None
