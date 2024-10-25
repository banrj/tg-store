from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.dto import shop as shop_dto
from app.db import utils as db_utils


class RefreshToken(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class ShopAuthData(BaseModel):
    shop: shop_dto.Shop
    tables: db_utils.SetupTablesConnection

    model_config = ConfigDict(arbitrary_types_allowed=True)