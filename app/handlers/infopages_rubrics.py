import datetime
import uuid
import logging

import fastapi
from boto3.dynamodb.conditions import Key, Attr

from app.settings import settings
from app.db import keys_structure as db_keys_structure, utils as db_utils, common as db_common, s3_key_structure
from app.dto import infopages_rubrics as dto_infopages_rubrics, common as dto_common
from app.dto.exceptions import common as exceptions_common, infopages_rubrics as exceptions_infopages_rubrics
from app.utils import s3 as s3_utils

logger = logging.getLogger(__name__)


def upload_rubric_background_img(shop_uuid, owner_uuid, file_uuid, image):
    image_extension = image.filename.split(".")[-1]
    bucket_url = s3_key_structure.infopages_rubric_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        file_uuid=file_uuid,
        image_extention=image_extension
    )
    image_url = s3_key_structure.infopages_rubric_image_url.format(
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


def handle_create_rubric(
        user_uuid: dto_common.UUIDasStr, owner_uuid: dto_common.UUIDasStr, shop_uuid: dto_common.UUIDasStr,
        data: dto_infopages_rubrics.RubricCreateRequest, image: fastapi.UploadFile | str) -> dto_infopages_rubrics.Rubric:
    rubric_uuid = uuid.uuid4()

    if bool(image):
        image_url = upload_rubric_background_img(
            shop_uuid=shop_uuid,
            owner_uuid=owner_uuid,
            file_uuid=uuid.uuid4(),
            image=image)
    else:
        image_url = None

    rubric_payload = dto_infopages_rubrics.Rubric(
        uuid_=rubric_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        title=data.title,
        description=data.description,
        inactive=False,
        date_create=datetime.datetime.now().isoformat(),
        hex_color=data.hex_color,
        sort_index=data.sort_index,
        image_url=image_url,
        record_type=db_keys_structure.infopages_rubrics_record_type,
    )
    rubric_payload._partkey = db_keys_structure.infopages_rubrics_partkey.format(shop_uuid=shop_uuid)
    rubric_payload._sortkey = db_keys_structure.infopages_rubrics_sortkey.format(rubric_uuid=rubric_uuid)

    db_utils.get_gen_table().put_item(Item=rubric_payload.to_record())

    return rubric_payload


def handle_update_rubric(
        user_uuid: dto_common.UUIDasStr, owner_uuid: dto_common.UUIDasStr, shop_uuid: dto_common.UUIDasStr,
        rubric_uuid: dto_common.UUIDasStr, data: dto_infopages_rubrics.RubricUpdateRequest,
        image: fastapi.UploadFile | str) -> dto_infopages_rubrics.Rubric:

    if bool(image) is False and bool(data.model_dump(exclude_none=True)) is False:
        raise exceptions_common.NoUpdateData

    if bool(image):
        image_url = upload_rubric_background_img(
            shop_uuid=shop_uuid,
            owner_uuid=owner_uuid,
            file_uuid=uuid.uuid4(),
            image=image)
    else:
        image_url = None

    rubric_payload = dto_infopages_rubrics.RubricUpdate(
        user_uuid=user_uuid,
        title=data.title,
        description=data.description,
        hex_color=data.hex_color,
        image_url=image_url,
        sort_index=data.sort_index,
    )
    rubric_payload._partkey = db_keys_structure.infopages_rubrics_partkey.format(shop_uuid=shop_uuid)
    rubric_payload._sortkey = db_keys_structure.infopages_rubrics_sortkey.format(rubric_uuid=rubric_uuid)

    rubric_updated = db_common.update_db_record(db_common.pydantic_db_update_helper(rubric_payload, return_values='ALL_OLD'))

    if image_url:
        s3_utils.delete_image_from_s3(image_url=rubric_updated['image_url'])

    rubric_updated.update(rubric_payload.to_record())

    return dto_infopages_rubrics.Rubric(**rubric_updated)


def handle_get_rubric(
        shop_uuid: dto_common.UUIDasStr, rubric_uuid: dto_common.UUIDasStr) -> dto_infopages_rubrics.Rubric:

    db_item = db_common.get_db_item(
        partkey=db_keys_structure.infopages_rubrics_partkey.format(shop_uuid=shop_uuid),
        sortkey=db_keys_structure.infopages_rubrics_sortkey.format(rubric_uuid=rubric_uuid)
    )
    if not db_item:
        raise exceptions_infopages_rubrics.RubricNotFound
    else:
        return dto_infopages_rubrics.Rubric(**db_item)


def handle_get_rubrics_list(shop_uuid: dto_common.UUIDasStr) -> list[dto_infopages_rubrics.Rubric]:
    pk = db_keys_structure.infopages_rubrics_partkey.format(shop_uuid=shop_uuid)
    rubrics_db: list = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(pk),
        filter_expression=Attr('inactive').eq(False)
    )

    return [dto_infopages_rubrics.Rubric(**r) for r in rubrics_db]


def handle_delete_rubric(
        user_uuid: dto_common.UUIDasStr, shop_uuid: dto_common.UUIDasStr, rubric_uuid: dto_common.UUIDasStr
) -> dto_common.ResponseNoBody:
    pk=db_keys_structure.infopages_rubrics_partkey.format(shop_uuid=shop_uuid)
    sk=db_keys_structure.infopages_rubrics_sortkey.format(rubric_uuid=rubric_uuid)
    db_common.change_inactive_status(pk=pk, sk=sk, user_uuid=user_uuid, inactive=True, return_values='NONE')

    return dto_common.ResponseNoBody()
