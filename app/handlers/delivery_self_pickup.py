import datetime
import uuid
import logging

import pydantic
from boto3.dynamodb.conditions import Key, Attr

from app.db import keys_structure as db_keys_structure, utils as db_utils, common as db_common
from app.dto import delivery_self_pickup as dto_delivery_self_pickup, user as dto_user, common as dto_common


logger = logging.getLogger(__name__)


def handle_create_delivery_self_pickup(
        user: dto_user.User, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4,
        data: dto_delivery_self_pickup.DeliverySelfPickupCreateRequest
) -> dto_delivery_self_pickup.DeliverySelfPickup:

    self_pickup_uuid = uuid.uuid4()

    self_pickup_payload = dto_delivery_self_pickup.DeliverySelfPickup(
        uuid_=self_pickup_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user.uuid_,
        shop_uuid=shop_uuid,
        title=data.title,
        description=data.description,
        contact_phone=data.contact_phone,
        contact_tg_username=data.contact_tg_username or user.tg_username,
        schedule=data.schedule,
        inactive=False,
        date_create=datetime.datetime.now().isoformat(),
        record_type=db_keys_structure.delivery_self_pickup_record_type,
    )
    self_pickup_payload._partkey = db_keys_structure.delivery_self_pickup_partkey.format(shop_uuid=shop_uuid)
    self_pickup_payload._sortkey = db_keys_structure.delivery_self_pickup_sortkey.format(
        self_pickup_uuid=self_pickup_uuid)
    db_utils.get_gen_table().put_item(Item=self_pickup_payload.to_record())

    return self_pickup_payload


def handle_update_delivery_self_pickup(
        user: dto_user.User, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, self_pickup_uuid: pydantic.UUID4,
        data: dto_delivery_self_pickup.DeliverySelfPickupUpdateRequest
) -> dto_delivery_self_pickup.DeliverySelfPickup:

    self_pickup_payload = dto_delivery_self_pickup.DeliverySelfPickupUpdate(
        user_uuid=user.uuid_,
        title=data.title,
        description=data.description,
        contact_phone=data.contact_phone,
        contact_tg_username=data.contact_tg_username,
        schedule=data.schedule,
    )
    self_pickup_payload._partkey = db_keys_structure.delivery_self_pickup_partkey.format(shop_uuid=shop_uuid)
    self_pickup_payload._sortkey = db_keys_structure.delivery_self_pickup_sortkey.format(
        self_pickup_uuid=self_pickup_uuid)
    result = db_common.update_db_record(db_common.pydantic_db_update_helper(self_pickup_payload))

    return dto_delivery_self_pickup.DeliverySelfPickup(**result)


def handle_get_delivery_self_pickup(
        shop_uuid: pydantic.UUID4, self_pickup_uuid: pydantic.UUID4
) -> dto_delivery_self_pickup.DeliverySelfPickup:

    pk = db_keys_structure.delivery_self_pickup_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.delivery_self_pickup_sortkey.format(
        self_pickup_uuid=self_pickup_uuid)
    result = db_common.get_db_item(partkey=pk, sortkey=sk)

    return dto_delivery_self_pickup.DeliverySelfPickup(**result)


def handle_get_list_of_delivery_self_pickup(
        shop_uuid: pydantic.UUID4) -> list[dto_delivery_self_pickup.DeliverySelfPickup]:

    pk = db_keys_structure.delivery_self_pickup_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.delivery_self_pickup_sortkey.format(self_pickup_uuid="")
    results = db_common.query_items_paged(
            key_condition_expression=Key('partkey').eq(pk) & Key('sortkey').begins_with(sk),
            filter_expression = Attr('inactive').eq(False)
    )

    return [dto_delivery_self_pickup.DeliverySelfPickup(**r) for r in results]


def handle_delete_delivery_self_pickup(
        user_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, self_pickup_uuid: pydantic.UUID4
) -> dto_common.ResponseNoBody:

    pk = db_keys_structure.delivery_self_pickup_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.delivery_self_pickup_sortkey.format(
        self_pickup_uuid=self_pickup_uuid)
    db_common.change_inactive_status(pk=pk, sk=sk, user_uuid=user_uuid, inactive=True, return_values='NONE')

    return dto_common.ResponseNoBody()
