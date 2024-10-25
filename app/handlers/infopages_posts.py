import datetime
import uuid
import logging

import fastapi
from boto3.dynamodb.conditions import Key, Attr, And

from app.settings import settings
from app.db import keys_structure as db_keys_structure, utils as db_utils, common as db_common, s3_key_structure
from app.dto import infopages_posts as dto_infopages_posts, common as dto_common
from app.dto.exceptions import common as exceptions_common, infopages_posts as exceptions_infopages_posts
from app.utils import s3 as s3_utils

logger = logging.getLogger(__name__)


def upload_post_images(shop_uuid, owner_uuid, post_uuid, images) -> list[str]:
    image_urls = []
    for image in images:
        image_extension = image.filename.split(".")[-1]

        bucket_url = s3_key_structure.infopages_post_file_path.format(
            owner_uuid=owner_uuid,
            shop_uuid=shop_uuid,
            post_uuid=post_uuid,
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


def handle_create_rubric(
        user_uuid: dto_common.UUIDasStr, owner_uuid: dto_common.UUIDasStr, shop_uuid: dto_common.UUIDasStr,
        data: dto_infopages_posts.PostCreateRequest, images: list[fastapi.UploadFile | str]) -> dto_infopages_posts.Post:
    post_uuid = uuid.uuid4()

    if bool(images):
        image_urls = upload_post_images(
            shop_uuid=shop_uuid,
            owner_uuid=owner_uuid,
            post_uuid=post_uuid,
            images=images)
    else:
        image_urls = None

    post_payload = dto_infopages_posts.Post(
        uuid_=post_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        rubric_uuid=data.rubric_uuid,
        title=data.title,
        description=data.description,
        inactive=False,
        date_create=datetime.datetime.now().isoformat(),
        image_urls=image_urls,
        record_type=db_keys_structure.infopages_posts_record_type,
    )
    post_payload._partkey = db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid)
    post_payload._sortkey = db_keys_structure.infopages_posts_sortkey.format(post_uuid=post_uuid)

    db_utils.get_gen_table().put_item(Item=post_payload.to_record())

    return post_payload


def handle_update_post(
        user_uuid: dto_common.UUIDasStr, owner_uuid: dto_common.UUIDasStr, shop_uuid: dto_common.UUIDasStr,
        post_uuid: dto_common.UUIDasStr, data: dto_infopages_posts.PostUpdateRequest,
        images: list[fastapi.UploadFile | str]) -> dto_infopages_posts.Post:

    if bool(images) is False and bool(data.model_dump(exclude_none=True)) is False:
        raise exceptions_common.NoUpdateData

    pk = db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.infopages_posts_sortkey.format(post_uuid=post_uuid)
    if len(data.image_urls) < 10:
        post_db_item = db_common.get_db_item(partkey=pk, sortkey=sk)
        if bool(post_db_item) is False:
            raise exceptions_infopages_posts.PostNotFound
        s3_utils.delete_different_images_from_s3(current_urls=post_db_item["image_urls"], new_urls=map(str, data.image_urls))

    if bool(images):
        image_urls = upload_post_images(
            shop_uuid=shop_uuid,
            owner_uuid=owner_uuid,
            post_uuid=post_uuid,
            images=images)
        data.image_urls.extend(image_urls)

    post_payload = dto_infopages_posts.PostUpdate(
        user_uuid=user_uuid,
        title=data.title,
        description=data.description,
        image_urls=data.image_urls,
        rubric_uuid=data.rubric_uuid,
        inactive=data.inactive,
    )
    post_payload._partkey = pk
    post_payload._sortkey = sk

    post_updated = db_common.update_db_record(db_common.pydantic_db_update_helper(post_payload))

    return dto_infopages_posts.Post(**post_updated)


def handle_get_post(
        shop_uuid: dto_common.UUIDasStr, post_uuid: dto_common.UUIDasStr) -> dto_infopages_posts.Post:

    db_item = db_common.get_db_item(
        partkey=db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid),
        sortkey=db_keys_structure.infopages_posts_sortkey.format(post_uuid=post_uuid)
    )
    if not db_item:
        raise exceptions_infopages_posts.PostNotFound
    else:
        return dto_infopages_posts.Post(**db_item)


def handle_get_shop_posts_list(shop_uuid: dto_common.UUIDasStr) -> list[dto_infopages_posts.Post]:
    pk = db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid)
    posts_db: list = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(pk),
        filter_expression=Attr('inactive').eq(False)
    )

    return [dto_infopages_posts.Post(**p) for p in posts_db]


def handle_get_rubric_posts_list(shop_uuid: dto_common.UUIDasStr, rubric_uuid: dto_common.UUIDasStr) -> list[dto_infopages_posts.Post]:
    pk = db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid)
    posts_db: list = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(pk),
        filter_expression=And(Attr('inactive').eq(False), Attr('rubric_uuid').eq(str(rubric_uuid)))
    )

    return [dto_infopages_posts.Post(**p) for p in posts_db]


def handle_delete_post(
        user_uuid: dto_common.UUIDasStr, shop_uuid: dto_common.UUIDasStr, post_uuid: dto_common.UUIDasStr
) -> dto_common.ResponseNoBody:
    pk=db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid)
    sk=db_keys_structure.infopages_posts_sortkey.format(post_uuid=post_uuid)
    db_common.change_inactive_status(pk=pk, sk=sk, user_uuid=user_uuid, inactive=True, return_values='NONE')

    return dto_common.ResponseNoBody()
