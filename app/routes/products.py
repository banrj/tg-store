import logging

import fastapi
from fastapi import status as http_status

from app.dto import (
    products as dto_products,
    common as dto_common,
    user as dto_user
)
from app.handlers import (
    auth as handlers_auth, products as handlers_products, product_variants as handlers_product_options
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/products", tags=['Products'])


@router.post(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_products.ProductBaseInfo,
)
def add_product_base_info(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        data: dto_products.ProductBaseInfoCreateRequest = fastapi.Body(...),
        image: fastapi.UploadFile | str = fastapi.File(None),
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить базовую информацию о товаре.
    """
    return handlers_products.handle_create_product_base_info(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        data=data,
        image=image,
    )


@router.patch(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}',
    response_model=dto_products.ProductBaseInfo,
)
def update_product_base_info(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        data: dto_products.ProductBaseInfoUpdateRequest = fastapi.Body(None),
        image: fastapi.UploadFile | str = fastapi.File(None),
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Изменить базовую информацию о товаре.
    """
    return handlers_products.handle_update_product_base_info(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        data=data,
        image=image,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}',
    response_model=dto_products.ProductBaseInfo,
)
def get_product_base_info(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить базовую информацию о товаре.
    """
    return handlers_products.handle_get_product_base_info(
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}/',
    response_model=list[dto_products.ProductBaseInfo],
)
def get_list_of_product_base_info(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить базовую информацию о всех товарах.
    """
    return handlers_products.handle_get_list_of_product_base_info(shop_uuid=shop_uuid)


@router.delete(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}',
    response_model=dto_common.ResponseNoBody,
)
def delete_product(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Удалить товар и все его сущности.
    """
    return handlers_products.handle_delete_product(
        user_uuid=auth_data.user.uuid_, shop_uuid=shop_uuid, product_uuid=product_uuid)
