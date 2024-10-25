import fastapi

from app.dto import (
    common as common_dto,
    shop as shop_dto
)
from app.handlers import shop as shop_handlers

router = fastapi.APIRouter(prefix="/shop")


# TODO добавить проверку API KEY
@router.get(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=shop_dto.Shop,
    tags=['Shop']
)
def get_shop(
        owner_uuid: common_dto.UUIDasStr,
        shop_uuid: common_dto.UUIDasStr
):
    """
    Получение информации о магазине
    """
    return shop_handlers.handle_get_shop(shop_uuid=shop_uuid, owner_uuid=owner_uuid)


# TODO добавить проверку API KEY
@router.get(
    path='/owner/{shop_uuid}',
    response_model=common_dto.UUIDasStr,
    tags=['Shop']
)
def get_owner_uuid_by_shop_uuid(
        shop_uuid: common_dto.UUIDasStr
):
    """
    Получение ID владельца по ID магазина
    """
    return shop_handlers.get_owner_uuid(shop_uuid=shop_uuid)


