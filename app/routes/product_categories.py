import logging

import fastapi

from app.dto import (
    product_categories as dto_product_categories,
    common as dto_common,
    user as user_dto
)
from app.handlers import product_categories as handlers_product_categories, auth as handlers_auth

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/product_categories", tags=['Product Categories'])


@router.post(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_product_categories.Category,
)
def add_product_category(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        data: dto_product_categories.CategoryCreateRequest = fastapi.Body(...),
        background_img: fastapi.UploadFile | str = fastapi.File(None),
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить категорию товаров.
    """
    return handlers_product_categories.handle_create_category(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        data=data,
        image=background_img,
    )


@router.patch(
    path='/{owner_uuid}/{shop_uuid}/{category_uuid}',
    response_model=dto_product_categories.Category,
)
def update_product_category(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        category_uuid: dto_common.UUIDasStr,
        data: dto_product_categories.CategoryUpdateRequest = fastapi.Body(None),
        background_img: fastapi.UploadFile | str = fastapi.File(None),
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить категорию товаров.
    """
    return handlers_product_categories.handle_update_category(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        category_uuid=category_uuid,
        data=data,
        image=background_img,
    )


@router.get(
    path='/{shop_uuid}',
    response_model=list[dto_product_categories.Category],
)
def get_product_categories_list(
        shop_uuid: dto_common.UUIDasStr,
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить список категорий товаров.
    """
    return handlers_product_categories.handle_get_categories_list(shop_uuid=shop_uuid)


@router.get(
    path='/{shop_uuid}/{category_uuid}',
    response_model=dto_product_categories.Category,
)
def get_product_category(
        shop_uuid: dto_common.UUIDasStr,
        category_uuid: dto_common.UUIDasStr,
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить информацию о категории товаров.
    """
    return handlers_product_categories.handle_get_category(shop_uuid=shop_uuid, category_uuid=category_uuid,)


@router.delete(path='/{shop_uuid}/{category_uuid}', response_model=dto_common.ResponseNoBody)
def delete_product_category(
        shop_uuid: dto_common.UUIDasStr,
        category_uuid: dto_common.UUIDasStr,
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Удалить (сделать неактивной) категорию товаров.
    """
    return handlers_product_categories.handle_delete_category(
        user_uuid=auth_data.user.uuid_, shop_uuid=shop_uuid, category_uuid=category_uuid)
