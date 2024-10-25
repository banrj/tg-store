import datetime
import uuid
import logging

import fastapi
import pydantic
from boto3.dynamodb.conditions import Key, Attr

from app.settings import settings
from app.db import keys_structure as db_keys_structure, utils as db_utils, common as db_common, s3_key_structure
from app.dto import product_variants as dto_product_variants, products as dto_products, common as dto_common
from app.dto.exceptions import products as exceptions_products
from app.utils import s3 as s3_utils

logger = logging.getLogger(__name__)


def upload_product_variant_images(shop_uuid, owner_uuid, product_uuid, variant_uuid, images) -> list[str]:
    image_urls = []
    for image in images:
        image_extension = image.filename.split(".")[-1]
        bucket_url = s3_key_structure.products_option_file_path.format(
            owner_uuid=owner_uuid,
            shop_uuid=shop_uuid,
            product_uuid=product_uuid,
            option_uuid=variant_uuid,
            file_uuid=uuid.uuid4(),
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
        image_urls.append(image_url)
    return image_urls


def update_product_minimal_price(
        user_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4):

    variants_pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    variants_sk = db_keys_structure.product_variant_sortkey.format(product_uuid=product_uuid, variant_uuid="")
    result: list = db_common.query_items_paged(
            key_condition_expression=Key('partkey').eq(variants_pk) & Key('sortkey').begins_with(variants_sk),
            filter_expression = Attr('inactive').eq(False),
            projection_expression='options'
    )
    if bool(result):
        product_minimal_price_payload = dto_products.ProductBaseInfoUpdateMinimalPrice(
            user_uuid=user_uuid,
            price=min([option.get('price', 0) for item in result for option in item.get('options', [])]),
        )
    else:
        product_minimal_price_payload = dto_products.ProductBaseInfoUpdateMinimalPrice(
            user_uuid=user_uuid,
            price=0,
        )
    product_minimal_price_payload._partkey = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    product_minimal_price_payload._sortkey = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)
    db_common.update_db_record(db_common.pydantic_db_update_helper(product_minimal_price_payload))


def handle_create_product_variant(
        user_uuid: pydantic.UUID4, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4,
        data: dto_product_variants.ProductVariantCreateRequest, images: list[fastapi.UploadFile] | str
) -> dto_product_variants.ProductVariant:

    variant_uuid = uuid.uuid4()

    if bool(images):
        image_urls = upload_product_variant_images(
            shop_uuid=shop_uuid,
            owner_uuid=owner_uuid,
            product_uuid=product_uuid,
            variant_uuid=variant_uuid,
            images=images)
    else:
        image_urls = None

    variant_payload = dto_product_variants.ProductVariant(
        uuid_=variant_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        title=data.title,
        image_urls=image_urls,
        options=[dto_product_variants.ProductVariantOption(**option.model_dump()) for option in data.options],
        inactive=False,
        date_create=datetime.datetime.now().isoformat(),
        record_type=db_keys_structure.product_variant_record_type,
    )
    variant_payload._partkey = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    variant_payload._sortkey = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=variant_uuid
    )
    db_utils.get_gen_table().put_item(Item=variant_payload.to_record())

    update_product_minimal_price(
        user_uuid=user_uuid, shop_uuid=shop_uuid, product_uuid=product_uuid)

    return variant_payload


def handle_update_product_variant(
        user_uuid: pydantic.UUID4, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4,
        variant_uuid: pydantic.UUID4, data: dto_product_variants.ProductVariantUpdateRequest,
        images: list[fastapi.UploadFile] | str
) -> dto_product_variants.ProductVariant:

    pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=variant_uuid
    )
    if len(data.image_urls) < 10:
        variant_db = db_common.get_db_item(partkey=pk, sortkey=sk)
        if bool(variant_db) is False:
            raise exceptions_products.VariantNotFound
        s3_utils.delete_different_images_from_s3(current_urls=variant_db["image_urls"], new_urls=map(str, data.image_urls))

    if bool(images):
        image_urls = upload_product_variant_images(
            shop_uuid=shop_uuid,
            owner_uuid=owner_uuid,
            product_uuid=product_uuid,
            variant_uuid=variant_uuid,
            images=images)
        data.image_urls.extend(image_urls)

    variant_payload = dto_product_variants.ProductVariantUpdate(
        user_uuid=user_uuid,
        title=data.title,
        image_urls=data.image_urls,
        options=[dto_product_variants.ProductVariantOption(**option.model_dump()) for option in data.options],
        inactive=False,
    )
    variant_payload._partkey = pk
    variant_payload._sortkey = sk
    result = db_common.update_db_record(db_common.pydantic_db_update_helper(variant_payload))

    update_product_minimal_price(user_uuid=user_uuid, shop_uuid=shop_uuid, product_uuid=product_uuid)

    return dto_product_variants.ProductVariant(**result)


def handle_get_product_variant(
        shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4, variant_uuid: pydantic.UUID4
) -> dto_product_variants.ProductVariant:

    pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=variant_uuid
    )
    variant_db = db_common.get_db_item(partkey=pk, sortkey=sk)
    if bool(variant_db) is False:
        raise exceptions_products.VariantNotFound
    return dto_product_variants.ProductVariant(**variant_db)


def handle_get_list_of_product_variants(
        shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4) -> list[dto_product_variants.ProductVariant]:

    pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_variant_sortkey.format(product_uuid=product_uuid, variant_uuid="")
    result: list = db_common.query_items_paged(
            key_condition_expression=Key('partkey').eq(pk) & Key('sortkey').begins_with(sk),
            filter_expression = Attr('inactive').eq(False)
    )

    variants = []
    for item in result:
        variants.append(dto_product_variants.ProductVariant(**item))

    return variants


def handle_delete_product_variant(
        user_uuid: pydantic.UUID4, owner_uuid: pydantic.UUID4, shop_uuid: pydantic.UUID4, product_uuid: pydantic.UUID4,
        variant_uuid: pydantic.UUID4
) -> dto_common.ResponseNoBody:

    pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=variant_uuid
    )
    result = db_common.change_inactive_status(pk=pk, sk=sk, user_uuid=user_uuid, inactive=True, return_values='NONE')

    update_product_minimal_price(
        user_uuid=user_uuid, shop_uuid=shop_uuid, product_uuid=product_uuid)

    return dto_common.ResponseNoBody()
