import uuid
import datetime

from unittest import mock
from boto3.dynamodb.conditions import Key

from app import settings
from app.dto import shop as dto_shop
from app.dto.exceptions import common as exceptions_common, shop as exceptions_shop
from app.db import utils as db_utils, common as db_common, keys_structure as db_keys_structure, s3_key_structure


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_create_shop(_mock_upload_file_to_s3, test_client, request):
    data = dto_shop.CreateShopRequest(
        title='test shop',
        description="Test Shop Description",
        shop_type="OnlineStore"
    )

    url = f'/shops'
    file = ('logotype', open("tests/utils/test.svg", "rb"))
    response = test_client.post(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()
    shop_uuid = response_body['uuid']

    pk = db_keys_structure.shop_partkey
    sk = db_keys_structure.shop_sortkey.format(shop_uuid=shop_uuid)
    shop_db = db_common.get_db_item(partkey=pk, sortkey=sk)

    product_category_db = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(db_keys_structure.product_category_partkey.format(shop_uuid=shop_uuid))
    )[0]

    logo_url_path = s3_key_structure.shop_file_path.format(
        shop_uuid=shop_uuid, file_uuid=uuid.uuid4(), photo_extention="svg"
    ).rsplit("/", 1)[0]

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': pk,
            'sortkey': sk
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': product_category_db["partkey"],
            'sortkey': product_category_db["sortkey"]
        })

    request.addfinalizer(resource_teardown)

    assert response_body["uuid"] == shop_db["uuid_"]
    assert response_body["title"] == shop_db["title"]
    assert response_body["owner_uuid"] == shop_db["owner_uuid"]
    assert response_body["description"] == shop_db["description"]
    assert response_body["subscription_active"] is True
    assert (datetime.datetime.fromisoformat(shop_db["subscription_expire_at"]) - datetime.datetime.now()).days - (settings.SHOP_TRIAL_DAYS - 1) == 0
    assert response_body["inactive"] is True
    assert shop_db["record_type"] == db_keys_structure.shop_record_type
    assert response_body["shop_type"] == shop_db["shop_type"]
    assert logo_url_path in response_body["logo_url"]
    assert logo_url_path in shop_db["logo_url"]
    assert _mock_upload_file_to_s3.call_count == 1

    assert product_category_db["title"] == "Все предложения"
    assert product_category_db["description"] == "Категория товаров по умолчанию."
    assert product_category_db["hex_color"] == "white"
    assert product_category_db.get("image_url", None) is None
    assert product_category_db["sort_index"] == 0
    assert product_category_db["record_type"] == db_keys_structure.product_category_record_type
    assert product_category_db["shop_uuid"] == shop_db["uuid_"]
    assert product_category_db["partkey"] == db_keys_structure.product_category_partkey.format(shop_uuid=shop_db["uuid_"])



@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_shop(_mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_inactive_shop, test_client, request):
    owner_uuid = str(insert_inactive_shop.owner_uuid)
    shop_uuid = str(insert_inactive_shop.uuid_)

    data = dto_shop.ShopUpdateRequest(
        title='Test Shop Updated',
        description="Test Shop Description",
        shop_type="InformationSite"
    )

    url = f'/shops/{owner_uuid}/{shop_uuid}'
    file = ('logotype', open("tests/utils/test.svg", "rb"))
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()

    logo_url_path = s3_key_structure.shop_file_path.format(
        shop_uuid=shop_uuid, file_uuid=uuid.uuid4(), photo_extention="svg"
    ).rsplit("/", 1)[0]

    assert response_body["uuid"] == str(insert_inactive_shop.uuid_)
    assert response_body["owner_uuid"] == str(insert_inactive_shop.owner_uuid)
    assert response_body["title"] == data.title
    assert response_body["description"] == data.description
    assert response_body["subscription_active"] is True
    assert (datetime.datetime.fromisoformat(response_body["subscription_expire_at"]) - datetime.datetime.now()).days - (settings.SHOP_TRIAL_DAYS - 1) == 0
    assert response_body["inactive"] is True
    assert response_body["shop_type"] == data.shop_type.value
    assert response_body["logo_url"] != str(insert_inactive_shop.logo_url)
    assert logo_url_path in response_body["logo_url"]
    assert _mock_upload_file_to_s3.call_count == 1
    assert _mock_delete_files_from_s3.call_count == 1


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_shop_without_image(_mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_inactive_shop, test_client, request):
    owner_uuid = str(insert_inactive_shop.owner_uuid)
    shop_uuid = str(insert_inactive_shop.uuid_)

    data = dto_shop.ShopUpdateRequest(
        title='Test Shop Updated',
        description="Test Shop Description",
        shop_type="InformationSite"
    )

    url = f'/shops/{owner_uuid}/{shop_uuid}'
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=None)
    response_body = response.json()

    logo_url_path = s3_key_structure.shop_file_path.format(
        shop_uuid=shop_uuid, file_uuid=uuid.uuid4(), photo_extention="svg"
    ).rsplit("/", 1)[0]

    assert response_body["uuid"] == str(insert_inactive_shop.uuid_)
    assert response_body["owner_uuid"] == str(insert_inactive_shop.owner_uuid)
    assert response_body["title"] == data.title
    assert response_body["description"] == data.description
    assert response_body["subscription_active"] is True
    assert (datetime.datetime.fromisoformat(response_body["subscription_expire_at"]) - datetime.datetime.now()).days - (settings.SHOP_TRIAL_DAYS - 1) == 0
    assert response_body["inactive"] is True
    assert response_body["shop_type"] == data.shop_type.value
    assert response_body["logo_url"] == str(insert_inactive_shop.logo_url)
    assert logo_url_path in response_body["logo_url"]
    assert _mock_upload_file_to_s3.call_count == 0
    assert _mock_delete_files_from_s3.call_count == 0


def test_update_shop_without_image_and_data(insert_inactive_shop, test_client, request):
    owner_uuid = str(insert_inactive_shop.owner_uuid)
    shop_uuid = str(insert_inactive_shop.uuid_)

    data = dto_shop.ShopUpdateRequest(
        title=None,
        description=None,
        shop_type=None
    )

    url = f'/shops/{owner_uuid}/{shop_uuid}'
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=None)
    response_body = response.json()

    assert response_body == exceptions_common.NoUpdateData.detail
    assert response.status_code == exceptions_common.NoUpdateData.status_code


def test_get_shop(insert_inactive_shop, test_client, request):
    owner_uuid = str(insert_inactive_shop.owner_uuid)
    shop_uuid = str(insert_inactive_shop.uuid_)

    url = f'/shops/{owner_uuid}/{shop_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body["uuid"] == str(insert_inactive_shop.uuid_)
    assert response_body["owner_uuid"] == str(insert_inactive_shop.owner_uuid)
    assert response_body["title"] == insert_inactive_shop.title
    assert response_body["description"] == insert_inactive_shop.description
    assert response_body["subscription_active"] is True
    assert (datetime.datetime.fromisoformat(response_body["subscription_expire_at"]) - datetime.datetime.now()).days - (settings.SHOP_TRIAL_DAYS - 1) == 0
    assert response_body["inactive"] is True
    assert response_body["shop_type"] == insert_inactive_shop.shop_type
    assert response_body["logo_url"] == str(insert_inactive_shop.logo_url)


def test_get_shop_list(insert_active_shop, insert_some_shops, test_client, request):
    owner_uuid = str(insert_some_shops.shop_first.owner_uuid)
    shop_uuid = str(insert_some_shops.shop_first.uuid_)

    url = f'/shops/{owner_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()
    shop_uuids = [r["uuid"] for r in response_body]

    assert len(response_body) == 3
    assert str(insert_some_shops.shop_first.uuid_) in shop_uuids
    assert str(insert_some_shops.shop_second.uuid_) in shop_uuids
    assert str(insert_some_shops.shop_inactive.uuid_) in shop_uuids


def test_delete_shop(insert_shop_same_owner_and_user, test_client, request):
    owner_uuid = str(insert_shop_same_owner_and_user.owner_uuid)
    shop_uuid = str(insert_shop_same_owner_and_user.uuid_)

    url = f'/shops/{owner_uuid}/{shop_uuid}'
    response = test_client.delete(url=url)

    pk = db_keys_structure.shop_partkey
    sk = db_keys_structure.shop_sortkey.format(shop_uuid=insert_shop_same_owner_and_user.uuid_)
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    assert response.status_code == 200
    assert db_item["uuid_"] == str(insert_shop_same_owner_and_user.uuid_)
    assert db_item["owner_uuid"] == str(insert_shop_same_owner_and_user.owner_uuid)
    assert db_item["title"] == insert_shop_same_owner_and_user.title
    assert db_item["description"] == insert_shop_same_owner_and_user.description
    assert db_item["subscription_active"] is True
    assert db_item["inactive"] is True
    assert db_item["shop_type"] == insert_shop_same_owner_and_user.shop_type
    assert db_item["logo_url"] == str(insert_shop_same_owner_and_user.logo_url)


def test_delete_shop_incorrect_owner(insert_active_shop, test_client, request):
    owner_uuid = str(insert_active_shop.owner_uuid)
    shop_uuid = str(insert_active_shop.uuid_)

    url = f'/shops/{owner_uuid}/{shop_uuid}'
    response = test_client.delete(url=url)
    response_body = response.json()

    assert response_body == exceptions_common.IncorrectOwner.detail
    assert response.status_code == exceptions_common.IncorrectOwner.status_code


def test_get_owner_uuid(insert_active_shop, test_client, request):
    shop_uuid = str(insert_active_shop.uuid_)

    url = f'/shops/owner_uuid/by/{shop_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body == str(insert_active_shop.owner_uuid)


def test_get_owner_uuid_incorrect_shop_uuid(test_client, request):
    url = f'/shops/owner_uuid/by/{uuid.uuid4()}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body == exceptions_shop.ShopNotFound.detail
    assert response.status_code == exceptions_shop.ShopNotFound.status_code
