import logging

import fastapi

from app.dto import (
    product_extra_kits as dto_product_extras,
    common as dto_common,
    user as dto_user
)
from app.handlers import (
    auth as handlers_auth, product_extra_kits as handlers_product_extra_kits
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/products/extra_kits", tags=['Product Extra Kits'])


@router.post(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}',
    response_model=dto_product_extras.ProductExtraKit,
)
def add_product_extra_kit(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        data: dto_product_extras.ProductExtraKitCreateRequest,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить дополнительный набор для товара.
    """
    return handlers_product_extra_kits.handle_create_product_extra_kit(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        data=data,
    )


@router.patch(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}/{extra_kit_uuid}',
    response_model=dto_product_extras.ProductExtraKit,
)
def update_product_extra_kit(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        extra_kit_uuid: dto_common.UUIDasStr,
        data: dto_product_extras.ProductExtraKitUpdateRequest,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Обновить дополнительный набор для товара.
    """
    return handlers_product_extra_kits.handle_update_product_extra_kit(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        extra_kit_uuid=extra_kit_uuid,
        data=data,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}/{extra_kit_uuid}',
    response_model=dto_product_extras.ProductExtraKit,
)
def get_product_extra_kit(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        extra_kit_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить дополнительный набор для товара.
    """
    return handlers_product_extra_kits.handle_get_product_extra_kit(
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        extra_kit_uuid=extra_kit_uuid,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}',
    response_model=list[dto_product_extras.ProductExtraKit],
)
def get_list_of_product_extra_kits(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить список дополнительных наборов для товара.
    """
    return handlers_product_extra_kits.handle_get_list_of_product_extra_kits(
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
    )


@router.delete(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}/{extra_kit_uuid}',
    response_model=dto_common.ResponseNoBody,
)
def make_inactive_product_extra_kit(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        extra_kit_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Удалить (сделать неактивным) дополнительный набор для товара.
    """
    return handlers_product_extra_kits.handle_delete_product_extra_kits(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        extra_kit_uuid=extra_kit_uuid,
    )
