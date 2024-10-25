import logging
import uuid
import fastapi

from app.dto import (
    user as dto_user,
    common as dto_common,
    shop as dto_shop,
)
from app.handlers import (
    auth as auth_handlers,
    shop as handlers_shop,
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/shops", tags=['Shop'])


@router.post(
    path='',
    response_model=dto_shop.Shop
)
def create_shop(
        data: dto_shop.CreateShopRequest = fastapi.Body(...),
        logotype: fastapi.UploadFile = fastapi.File(...),
        auth_data: dto_user.AuthData = fastapi.Depends(auth_handlers.auth_user),
):
    """
    Создать магазин
    """
    return handlers_shop.handle_create_shop(data=data, image=logotype, owner_uuid=auth_data.user.uuid_)


@router.patch(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_shop.Shop
)
def update_shop(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        data: dto_shop.ShopUpdateRequest = fastapi.Body(None),
        logotype: fastapi.UploadFile | str = fastapi.File(None),
        auth_data: dto_user.AuthData = fastapi.Depends(auth_handlers.auth_user)
):
    """
    Обновить магазин
    """
    return handlers_shop.handle_update_shop(
        user_uuid=auth_data.user.uuid_, owner_uuid=owner_uuid, shop_uuid=shop_uuid, data=data, image=logotype)


@router.get(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_shop.Shop
)
def get_shop(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(auth_handlers.auth_user)
):
    """
    Получение информации о магазине
    """
    return handlers_shop.handle_get_shop(shop_uuid=shop_uuid, owner_uuid=owner_uuid)


@router.delete(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_common.ResponseNoBody
)
def delete_shop(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(auth_handlers.auth_user)
):
    """
    Удаление магазина. Делаем неактивным.
    """
    return handlers_shop.handle_delete_shop(user_uuid=auth_data.user.uuid_, owner_uuid=owner_uuid, shop_uuid=shop_uuid)


@router.get(
    path='/{owner_uuid}',
    response_model=list[dto_shop.Shop]
)
def get_shop_list(owner_uuid: dto_common.UUIDasStr, auth_data: dto_user.AuthData = fastapi.Depends(auth_handlers.auth_user)):
    """
    Получение списка всех магазинов
    """
    return handlers_shop.handle_get_shop_list(owner_uuid=owner_uuid)


@router.get(
    path='/owner_uuid/by/{shop_uuid}',
    response_model=uuid.UUID
)
def get_owner_uuid_by_shop_uuid(
        shop_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(auth_handlers.auth_user)
):
    """
    Получение ID владельца по ID магазина
    """
    return handlers_shop.get_owner_uuid(shop_uuid=shop_uuid)
