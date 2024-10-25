import datetime
import uuid
import logging

import fastapi
import pydantic
from boto3.dynamodb.conditions import Key, Attr, And

from app.settings import settings
from app.db import keys_structure as db_keys_structure, utils as db_utils, common as db_common, s3_key_structure
from app.dto import products as dto_products, common as dto_common
from app.dto.exceptions import common as exceptions_common, products as exceptions_products
from app.utils import s3 as s3_utils

logger = logging.getLogger(__name__)


def upload_product_base_image(shop_uuid, owner_uuid, product_uuid, file_uuid, image) -> str:
    image_extension = image.filename.split(".")[-1]

    bucket_url = s3_key_structure.products_base_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        file_uuid=file_uuid,
        image_extention=image_extension
    )
    image_url = s3_key_structure.product_category_image_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
        file_name=bucket_url
    )
    s3_utils.upload_file_to_s3(
        bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
        bucket_url=bucket_url,
        file=image
    )
    return image_url


def handle_create_product_base_info(
        user_uuid: pydantic.UUID4, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4,
        data: dto_products.ProductBaseInfoCreateRequest, image: fastapi.UploadFile | str
) -> dto_products.ProductBaseInfo:

    product_uuid = uuid.uuid4()

    if bool(image):
        image_url = upload_product_base_image(
            shop_uuid=shop_uuid,
            owner_uuid=owner_uuid,
            product_uuid=product_uuid,
            file_uuid=uuid.uuid4(),
            image=image)
    else:
        raise exceptions_products.FileRequired

    product_payload = dto_products.ProductBaseInfo(
        uuid_=product_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        title=data.title,
        description=data.description,
        category_uuids=data.category_uuids,
        inactive=False,
        date_create=datetime.datetime.now().isoformat(),
        image_url=image_url,
        record_type=db_keys_structure.product_base_record_type,
    )
    product_payload._partkey = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    product_payload._sortkey = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)

    db_utils.get_gen_table().put_item(Item=product_payload.to_record())

    return product_payload


def handle_update_product_base_info(
        user_uuid: pydantic.UUID4, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4,
        data: dto_products.ProductBaseInfoUpdateRequest, image: fastapi.UploadFile | str
) -> dto_products.ProductBaseInfo:

    if bool(image) is False and bool(data.model_dump(exclude_none=True)) is False:
        raise exceptions_common.NoUpdateData

    if bool(image):
        image_url = upload_product_base_image(
            shop_uuid=shop_uuid,
            owner_uuid=owner_uuid,
            product_uuid=product_uuid,
            file_uuid=uuid.uuid4(),
            image=image)
    else:
        image_url = None

    product_payload = dto_products.ProductBaseInfoUpdate(
        user_uuid=user_uuid,
        title=data.title,
        description=data.description,
        category_uuids=data.category_uuids,
        image_url=image_url,
        inactive=data.inactive,
    )
    product_payload._partkey = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    product_payload._sortkey = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)

    product_updated = db_common.update_db_record(db_common.pydantic_db_update_helper(product_payload, return_values='ALL_OLD'))

    if image_url:
        s3_utils.delete_image_from_s3(image_url=product_updated['image_url'])

    product_updated.update(product_payload.to_record())

    return dto_products.ProductBaseInfo(**product_updated)


def handle_get_product_base_info(shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4,) -> dto_products.ProductBaseInfo:

    pk = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)

    product_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    if bool(product_item) is False:
        raise exceptions_products.ProductNotFound

    return dto_products.ProductBaseInfo(**product_item)


def handle_get_list_of_product_base_info(shop_uuid: pydantic.UUID4) -> list[dto_products.ProductBaseInfo]:
    pk = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)

    product_items = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(pk),
        filter_expression=And(
            Attr('inactive').eq(False), Attr('record_type').eq(db_keys_structure.product_base_record_type)
        )
    )
    return [dto_products.ProductBaseInfo(**item) for item in product_items]


def handle_delete_product(
        user_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4
) -> dto_common.ResponseNoBody:

    pk = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    product_items = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(pk) & Key('sortkey').begins_with(str(product_uuid)),
        filter_expression=Attr('inactive').eq(False),
        projection_expression='partkey, sortkey'
    )

    for item in product_items:
        db_common.change_inactive_status(
            pk=item['partkey'], sk=item['sortkey'], user_uuid=str(user_uuid), inactive=True, return_values='NONE')

    return dto_common.ResponseNoBody()
