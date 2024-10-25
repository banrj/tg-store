from app.dto import common as dto_common


class Post(dto_common.TGStoreShopEntitiesBaseModel):
    title: str
    description: str
    image_urls: list[dto_common.StrUrl]
    rubric_uuid: dto_common.UUIDasStr


class PostCreateRequest(dto_common.TGStoreBaseRequest):
    title: str
    description: str
    rubric_uuid: dto_common.UUIDasStr


class PostUpdateRequest(dto_common.TGStoreBaseRequest):
    title: str | None = None
    description: str | None = None
    image_urls: list[dto_common.StrUrl] | None = None
    rubric_uuid: dto_common.UUIDasStr | None = None
    inactive: bool | None = None


class PostUpdate(dto_common.TGStoreEntityBaseUpdateModel, PostUpdateRequest):
    pass
