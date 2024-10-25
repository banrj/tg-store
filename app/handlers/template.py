import uuid
import datetime

import fastapi
from boto3.dynamodb.conditions import Key
import logging

from app import settings
from app.dto import template as template_dto, common as common_dto
from app.utils import s3 as s3_utils
from app.db import utils as db_utils, keys_structure as db_keys_structure, common as db_common, s3_key_structure
from app.dto import common as dto_common

logger = logging.getLogger(__name__)


def upload_template_photo(photo, template_uuid):
    photo_extension = photo.filename.split(".")[-1]
    bucket_url = s3_key_structure.template_file_path.format(template_uuid=template_uuid, photo_extention=photo_extension)
    photo_url = s3_key_structure.template_photo_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_SERVICE_BUCKET_NAME,
        file_name=bucket_url
    )
    s3_utils.upload_file_to_s3(
        bucket_name=settings.YC_SERVICE_BUCKET_NAME,
        bucket_url=bucket_url,
        file=photo
    )
    return photo_url


def handle_add_template(data: template_dto.TemplateRequestBody, photo: fastapi.UploadFile) -> template_dto.Template:
    template_uuid = uuid.uuid4()
    photo_url = upload_template_photo(photo, template_uuid)
    template = template_dto.Template(
        uuid_=template_uuid,
        title=data.title,
        description=data.description,
        photo_url=photo_url,
        template_url=data.template_url,
        exclusive_owner_uuid=data.exclusive_owner_uuid or None,
        date_create=datetime.datetime.now().isoformat(),
        record_type=db_keys_structure.template_record_type
    )
    template._partkey = db_keys_structure.template_partkey
    template._sortkey = db_keys_structure.template_sortkey.format(uuid=template.uuid_)

    db_utils.get_gen_table().put_item(Item=template.to_record())
    return template


def handle_update_template(
        template_uuid: common_dto.UUIDasStr,
        data: template_dto.TemplateUpdateBody,
        photo: fastapi.UploadFile | str
) -> template_dto.Template:

    if bool(photo):
        photo_url = upload_template_photo(photo, template_uuid)
    else:
        photo_url = None

    pk = db_keys_structure.template_partkey
    sk = db_keys_structure.template_sortkey.format(uuid=template_uuid)
    if data.model_dump(exclude_none=True):
        data._partkey = pk
        data._sortkey = sk
        template = template_dto.Template(**db_common.update_db_record(db_common.pydantic_db_update_helper(data)))
    else:
        template = template_dto.Template(**db_common.get_db_item(partkey=pk, sortkey=sk))

    return template


def handle_get_list_templates() -> list[template_dto.Template]:
    templates = db_common.query_items_paged(key_condition_expression=Key('partkey').eq(db_keys_structure.template_partkey))
    return [template_dto.Template(**t) for t in templates]


def handle_get_template(template_uuid: str) -> template_dto.Template:
    template_item = db_common.get_db_item(
        partkey=db_keys_structure.template_partkey,
        sortkey=db_keys_structure.template_sortkey.format(uuid=template_uuid)
    )
    return template_dto.Template(**template_item)


def delete_template_request(pk: str, sk: str) -> dict:
    logger.info(f"delete_template_request ::: make inactive template: partkey={pk}, sortkey={sk}")
    return db_utils.get_gen_table().update_item(
        Key={
            'partkey': pk,
            'sortkey': sk
        },
        UpdateExpression=f"set {'inactive'} = :value",
        ExpressionAttributeValues={':value': True},
        ReturnValues="ALL_NEW"
    )["Attributes"]


def handle_delete_template(template_uuid: dto_common.UUIDasStr) -> template_dto.Template:
    pk = db_keys_structure.template_partkey
    sk = db_keys_structure.template_sortkey.format(uuid=template_uuid)

    shop_updated = delete_template_request(pk=pk, sk=sk)
    logger.info(f"delete_shop_db_request ::: shop deactivated: partkey={pk}, sortkey={sk}")

    return template_dto.Template(**shop_updated)


