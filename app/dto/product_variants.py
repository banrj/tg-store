import pydantic
import decimal

from app.dto import common as dto_common


class ProductVariantOption(pydantic.BaseModel):
    title: str
    article: str
    price: decimal.Decimal
    weight: int
    quantity: int


class ProductVariant(dto_common.TGStoreShopProductsBaseModel):
    title: str
    options: list[ProductVariantOption]
    image_urls: list[dto_common.StrUrl] | None = None


class ProductVariantCreateRequest(dto_common.TGStoreBaseRequest):
    title: str
    options: list[ProductVariantOption]


class ProductVariantUpdateRequest(dto_common.TGStoreBaseRequest):
    title: str | None = None
    options: list[ProductVariantOption] | None = None
    image_urls: list[dto_common.StrUrl] | None = None
    inactive: bool | None = None


class ProductVariantUpdate(dto_common.TGStoreEntityBaseUpdateModel, ProductVariantUpdateRequest):
    pass
