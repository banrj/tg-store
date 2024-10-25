from app.dto import common as dto_common


class Category(dto_common.TGStoreShopEntitiesBaseModel):
    title: str
    description: str | None = None
    image_url: dto_common.StrUrl | None = None
    hex_color: dto_common.StrColor = "FFFFFF"
    sort_index: int | None = 1


class CategoryCreateRequest(dto_common.TGStoreBaseRequest):
    title: str
    description: str | None = None
    hex_color: dto_common.StrColor = "FFFFFF"
    sort_index: int = 1


class CategoryUpdateRequest(dto_common.TGStoreBaseRequest):
    title: str | None = None
    description: str | None = None
    hex_color: dto_common.StrColor | None = None
    sort_index: int | None = None


class CategoryUpdate(dto_common.TGStoreEntityBaseUpdateModel, CategoryUpdateRequest):
    image_url: dto_common.StrUrl | None = None
    inactive: bool | None = None
