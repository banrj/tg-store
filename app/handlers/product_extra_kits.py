import datetime
import uuid
import logging

import pydantic
from boto3.dynamodb.conditions import Key, Attr

from app.db import keys_structure as db_keys_structure, utils as db_utils, common as db_common
from app.dto import product_extra_kits as dto_product_extra_kits, common as dto_common
from app.dto.exceptions import products as exceptions_products


logger = logging.getLogger(__name__)


def handle_create_product_extra_kit(
        user_uuid: pydantic.UUID4, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4,
        data: dto_product_extra_kits.ProductExtraKitCreateRequest
) -> dto_product_extra_kits.ProductExtraKit:

    extra_kit_uuid = uuid.uuid4()

    extra_kit_payload = dto_product_extra_kits.ProductExtraKit(
        uuid_=extra_kit_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        title=data.title,
        price=data.price,
        addons=data.addons,
        inactive=False,
        date_create=datetime.datetime.now().isoformat(),
        record_type=db_keys_structure.product_extra_kits_record_type,
    )
    extra_kit_payload._partkey = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    extra_kit_payload._sortkey = db_keys_structure.product_extra_kits_sortkey.format(
        product_uuid=product_uuid, extra_kit_uuid=extra_kit_uuid
    )

    db_utils.get_gen_table().put_item(Item=extra_kit_payload.to_record())

    return extra_kit_payload


def handle_update_product_extra_kit(
        user_uuid: pydantic.UUID4, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4,
        extra_kit_uuid: pydantic.UUID4, data: dto_product_extra_kits.ProductExtraKitUpdateRequest
) -> dto_product_extra_kits.ProductExtraKit:

    extra_kit_payload = dto_product_extra_kits.ProductExtraKitUpdate(
        user_uuid=user_uuid,
        title=data.title,
        price=data.price,
        addons=data.addons,
    )
    extra_kit_payload._partkey = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    extra_kit_payload._sortkey = db_keys_structure.product_extra_kits_sortkey.format(
        product_uuid=product_uuid, extra_kit_uuid=extra_kit_uuid
    )

    result = db_common.update_db_record(db_common.pydantic_db_update_helper(extra_kit_payload))

    return dto_product_extra_kits.ProductExtraKit(**result)


def handle_get_product_extra_kit(
        shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4, extra_kit_uuid: pydantic.UUID4
) -> dto_product_extra_kits.ProductExtraKit:

    pk = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_extra_kits_sortkey.format(
        product_uuid=product_uuid, extra_kit_uuid=extra_kit_uuid
    )
    variant_db = db_common.get_db_item(partkey=pk, sortkey=sk)
    if bool(variant_db) is False:
        raise exceptions_products.ExtraKitNotFound
    return dto_product_extra_kits.ProductExtraKit(**variant_db)


def handle_get_list_of_product_extra_kits(
        shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4) -> list[dto_product_extra_kits.ProductExtraKit]:

    pk = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_extra_kits_sortkey.format(product_uuid=product_uuid, extra_kit_uuid="")
    result: list = db_common.query_items_paged(
            key_condition_expression=Key('partkey').eq(pk) & Key('sortkey').begins_with(sk),
            filter_expression = Attr('inactive').eq(False)
    )

    extra_kits = []
    for item in result:
        extra_kits.append(dto_product_extra_kits.ProductExtraKit(**item))

    return extra_kits


def handle_delete_product_extra_kits(
        user_uuid: pydantic.UUID4, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4,
        extra_kit_uuid: pydantic.UUID4
) -> dto_common.ResponseNoBody:

    pk = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_extra_kits_sortkey.format(
        product_uuid=product_uuid, extra_kit_uuid=extra_kit_uuid
    )
    db_common.change_inactive_status(pk=pk, sk=sk, user_uuid=user_uuid, inactive=True, return_values='NONE')

    return dto_common.ResponseNoBody()
