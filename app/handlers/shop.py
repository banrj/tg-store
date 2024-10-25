import datetime
import uuid
import logging

import fastapi
import pydantic
from boto3.dynamodb.conditions import Key, Attr

from app.settings import settings
from app.db import keys_structure as db_keys_structure, utils as db_utils, common as db_common, s3_key_structure
from app.dto import shop as shop_dto, common as dto_common, product_categories as dto_product_categories
from app.handlers import product_categories as handlers_product_categories
from app.dto.exceptions import shop as shop_exceptions, common as exceptions_common
from app.utils import s3 as s3_utils

logger = logging.getLogger(__name__)


def upload_shop_logo(photo, shop_uuid):
    photo_extension = photo.filename.split(".")[-1]
    bucket_url = s3_key_structure.shop_file_path.format(
        shop_uuid=shop_uuid, file_uuid=uuid.uuid4(), photo_extention=photo_extension)
    photo_url = s3_key_structure.shop_logo_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
        file_name=bucket_url
    )
    s3_utils.upload_file_to_s3(
        bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
        bucket_url=bucket_url,
        file=photo
    )
    return photo_url


def trial_period_for_new_shop():
    # Возвращает дату окончания триального периода
    return (datetime.datetime.now() + datetime.timedelta(days=settings.SHOP_TRIAL_DAYS)).isoformat()


def handle_create_shop(
        data: shop_dto.CreateShopRequest, image: fastapi.UploadFile, owner_uuid: dto_common.UUIDasStr) -> shop_dto.Shop:
    shop_uuid = uuid.uuid4()
    shop_payload = shop_dto.Shop(
        uuid_=shop_uuid,
        user_uuid=owner_uuid,
        owner_uuid=owner_uuid,
        title=data.title,
        description=data.description,
        subscription_active=True,
        subscription_expire_at=trial_period_for_new_shop(),
        inactive=True,
        shop_type=data.shop_type,
        date_create=datetime.datetime.now().isoformat(),
        logo_url=upload_shop_logo(image, shop_uuid),
        record_type=db_keys_structure.shop_record_type,
    )
    shop_payload._partkey = db_keys_structure.shop_partkey
    shop_payload._sortkey = db_keys_structure.shop_sortkey.format(shop_uuid=shop_payload.uuid_)
    db_utils.get_gen_table().put_item(Item=shop_payload.to_record())

    data_product_category = dto_product_categories.CategoryCreateRequest(
        title="Все предложения",
        description="Категория товаров по умолчанию.",
        sort_index=0,
    )
    handlers_product_categories.handle_create_category(
        user_uuid=owner_uuid, owner_uuid=owner_uuid, shop_uuid=shop_payload.uuid_,
        data=data_product_category, image= ''
    )

    return shop_payload


def handle_update_shop(
        user_uuid: dto_common.UUIDasStr,
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        data: shop_dto.ShopUpdateRequest,
        image: fastapi.UploadFile | str,
) -> shop_dto.Shop:

    if bool(image) is False and bool(data.model_dump(exclude_none=True)) is False:
        raise exceptions_common.NoUpdateData

    if bool(image):
        logo_url = upload_shop_logo(image, shop_uuid)
    else:
        logo_url = None

    shop_payload = shop_dto.ShopUpdate(
        user_uuid=user_uuid,
        title=data.title,
        description=data.description,
        inactive=None,
        shop_type=data.shop_type,
        logo_url=logo_url,
        template_uuid=data.template_uuid,
    )
    shop_payload._partkey = db_keys_structure.shop_partkey
    shop_payload._sortkey = db_keys_structure.shop_sortkey.format(shop_uuid=shop_uuid)
    shop_updated: dict = db_common.update_db_record(db_common.pydantic_db_update_helper(shop_payload, return_values='ALL_OLD'))

    if logo_url:
        s3_utils.delete_image_from_s3(image_url=shop_updated['logo_url'])

    shop_updated.update(shop_payload.to_record())

    return shop_dto.Shop(**shop_updated)


def handle_get_shop(shop_uuid: dto_common.UUIDasStr, owner_uuid: dto_common.UUIDasStr) -> shop_dto.Shop:
    shop_db = db_common.get_db_item(
        partkey=db_keys_structure.shop_partkey,
        sortkey=db_keys_structure.shop_sortkey.format(shop_uuid=shop_uuid)
    )
    if not shop_db:
        raise shop_exceptions.ShopNotFound
    else:
        return shop_dto.Shop(**shop_db)


def handle_get_shop_list(owner_uuid: dto_common.UUIDasStr) -> list[shop_dto.Shop]:
    pk = db_keys_structure.shop_partkey
    shop_list_db: list = db_common.query_items_paged(
            key_condition_expression=Key('partkey').eq(pk),
            filter_expression=Attr('owner_uuid').eq(str(owner_uuid)),
    )

    shop_list = []
    for shop_item in shop_list_db:
        shop_list.append(shop_dto.Shop(**shop_item))

    return shop_list


def handle_delete_shop(
        user_uuid: pydantic.UUID4,
        owner_uuid: pydantic.UUID4,
        shop_uuid: pydantic.UUID4,
) -> dto_common.ResponseNoBody:
    pk = db_keys_structure.shop_partkey
    sk = db_keys_structure.shop_sortkey.format(shop_uuid=shop_uuid)

    db_common.change_inactive_status_by_owner(pk=pk, sk=sk, user_uuid=str(user_uuid), inactive=True, return_values='NONE')
    logger.info(f"delete_shop_db_request ::: shop deactivated: partkey={pk}, sortkey={sk}")

    return dto_common.ResponseNoBody()


def get_owner_uuid(shop_uuid: str) -> uuid.UUID:
    shop_item = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(db_keys_structure.shop_partkey),
        filter_expression=Attr('uuid_').eq(str(shop_uuid)),
        projection_expression='owner_uuid'
    )
    if shop_item:
        return shop_item[0]["owner_uuid"]
    else:
        raise shop_exceptions.ShopNotFound
