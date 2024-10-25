from app.dto import common as dto_common


class Rubric(dto_common.TGStoreShopEntitiesBaseModel):
    title: str
    description: str | None = None
    image_url: dto_common.StrUrl | None = None
    hex_color: dto_common.StrColor = "FFFFFF"
    sort_index: int | None = 1


class RubricCreateRequest(dto_common.TGStoreBaseRequest):
    title: str
    description: str | None = None
    hex_color: dto_common.StrColor = "FFFFFF"
    sort_index: int = 1


class RubricUpdateRequest(dto_common.TGStoreBaseRequest):
    title: str | None = None
    description: str | None = None
    hex_color: dto_common.StrColor | None = None
    sort_index: int | None = None


class RubricUpdate(dto_common.TGStoreEntityBaseUpdateModel, RubricUpdateRequest):
    image_url: dto_common.StrUrl | None = None
