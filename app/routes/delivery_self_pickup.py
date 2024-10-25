import logging

import fastapi

from app.dto import (
    delivery_self_pickup as dto_delivery_self_pickup,
    common as dto_common,
    user as dto_user
)
from app.handlers import (
    auth as handlers_auth, delivery_self_pickup as handlers_delivery_self_pickup
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/delivery/self_pickup", tags=['Delivery Self Pickup'])


@router.post(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_delivery_self_pickup.DeliverySelfPickup,
)
def add_delivery_self_pickup(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        data: dto_delivery_self_pickup.DeliverySelfPickupCreateRequest,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить вариант самовывоза товара.
    """
    return handlers_delivery_self_pickup.handle_create_delivery_self_pickup(
        user=auth_data.user,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        data=data,
    )


@router.patch(
    path='/{owner_uuid}/{shop_uuid}/{self_pickup_uuid}',
    response_model=dto_delivery_self_pickup.DeliverySelfPickup,
)
def update_delivery_self_pickup(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        self_pickup_uuid: dto_common.UUIDasStr,
        data: dto_delivery_self_pickup.DeliverySelfPickupUpdateRequest,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Обновить вариант самовывоза товара.
    """
    return handlers_delivery_self_pickup.handle_update_delivery_self_pickup(
        user=auth_data.user,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        self_pickup_uuid=self_pickup_uuid,
        data=data,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}/{self_pickup_uuid}',
    response_model=dto_delivery_self_pickup.DeliverySelfPickup,
)
def get_delivery_self_pickup(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        self_pickup_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить данные для варианта самовывоза товара.
    """
    return handlers_delivery_self_pickup.handle_get_delivery_self_pickup(
        shop_uuid=shop_uuid,
        self_pickup_uuid=self_pickup_uuid,
    )


@router.get(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=list[dto_delivery_self_pickup.DeliverySelfPickup],
)
def get_list_of_delivery_self_pickup(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить список вариантов самовывоза товара.
    """
    return handlers_delivery_self_pickup.handle_get_list_of_delivery_self_pickup(shop_uuid=shop_uuid)


@router.delete(path='/{owner_uuid}/{shop_uuid}/{self_pickup_uuid}', response_model=dto_common.ResponseNoBody)
def delete_delivery_self_pickup(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        self_pickup_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Удалить вариант самовывоза товара.
    """
    return handlers_delivery_self_pickup.handle_delete_delivery_self_pickup(
        user_uuid=auth_data.user.uuid_,
        shop_uuid=shop_uuid,
        self_pickup_uuid=self_pickup_uuid,
    )
