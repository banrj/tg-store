import logging

import fastapi

from app.dto import (
    delivery_manual as dto_delivery_manual,
    common as dto_common,
    user as dto_user
)
from app.handlers import (
    auth as handlers_auth, delivery_manual as handlers_delivery_manual
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/delivery/manual", tags=['Delivery Manual'])


@router.post(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_delivery_manual.DeliveryManual,
)
def add_delivery_manual(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        data: dto_delivery_manual.DeliveryManualCreateRequest,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить вариант ручной доставки товара.
    """
    return handlers_delivery_manual.handle_create_delivery_manual(
        user=auth_data.user,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        data=data,
    )


@router.patch(
    path='/{owner_uuid}/{shop_uuid}/{delivery_manual_uuid}',
    response_model=dto_delivery_manual.DeliveryManual,
)
def update_delivery_manual(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        delivery_manual_uuid: dto_common.UUIDasStr,
        data: dto_delivery_manual.DeliveryManualUpdateRequest,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Обновить вариант ручной доставки товара.
    """
    return handlers_delivery_manual.handle_update_delivery_manual(
        user=auth_data.user,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        delivery_manual_uuid=delivery_manual_uuid,
        data=data,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}/{delivery_manual_uuid}',
    response_model=dto_delivery_manual.DeliveryManual,
)
def get_delivery_manual(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        delivery_manual_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить данные для варианта ручной доставки товара.
    """
    return handlers_delivery_manual.handle_get_delivery_manual(
        shop_uuid=shop_uuid,
        delivery_manual_uuid=delivery_manual_uuid,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=list[dto_delivery_manual.DeliveryManual],
)
def get_list_of_delivery_manual(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить список вариантов ручной доставки товара.
    """
    return handlers_delivery_manual.handle_get_list_of_delivery_manual(shop_uuid=shop_uuid)


@router.delete(path='/{owner_uuid}/{shop_uuid}/{delivery_manual_uuid}', response_model=dto_common.ResponseNoBody)
def delete_delivery_manual(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        delivery_manual_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Удалить вариант ручной доставки товара.
    """
    return handlers_delivery_manual.handle_delete_delivery_manual(
        user_uuid=auth_data.user.uuid_,
        shop_uuid=shop_uuid,
        delivery_manual_uuid=delivery_manual_uuid,
    )
