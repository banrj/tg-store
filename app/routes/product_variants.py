import logging
from typing import List

import fastapi

from app.dto import (
    product_variants as dto_product_variants,
    common as dto_common,
    user as dto_user
)
from app.handlers import (
    auth as handlers_auth, product_variants as handlers_product_variants
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/products/variants", tags=['Product Variants'])


@router.post(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}',
    response_model=dto_product_variants.ProductVariant,
)
def add_product_variant(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        data: dto_product_variants.ProductVariantCreateRequest = fastapi.Body(None),
        images: List[fastapi.UploadFile] = fastapi.File(None),
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить вариант товара.
    """
    return handlers_product_variants.handle_create_product_variant(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        data=data,
        images=images,
    )


@router.patch(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}/{variant_uuid}',
    response_model=dto_product_variants.ProductVariant,
)
def update_product_variant(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        variant_uuid: dto_common.UUIDasStr,
        data: dto_product_variants.ProductVariantUpdateRequest = fastapi.Body(None),
        images: List[fastapi.UploadFile] = fastapi.File(None),
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Изменить вариант товара.
    """
    return handlers_product_variants.handle_update_product_variant(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        variant_uuid=variant_uuid,
        data=data,
        images=images,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}/{variant_uuid}',
    response_model=dto_product_variants.ProductVariant,
)
def get_product_variant(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        variant_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить вариант товара.
    """
    return handlers_product_variants.handle_get_product_variant(
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        variant_uuid=variant_uuid,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}',
    response_model=list[dto_product_variants.ProductVariant],
)
def get_list_of_product_variants(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить все варианты товара.
    """
    return handlers_product_variants.handle_get_list_of_product_variants(
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
    )


@router.delete(
    path='/{owner_uuid}/{shop_uuid}/{product_uuid}/{variant_uuid}',
    response_model=dto_common.ResponseNoBody,
)
def make_inactive_product_variant(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        product_uuid: dto_common.UUIDasStr,
        variant_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Удалить (сделать неактивным) вариант товара.
    """
    return handlers_product_variants.handle_delete_product_variant(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        variant_uuid=variant_uuid,
    )
