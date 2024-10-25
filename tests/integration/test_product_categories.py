import uuid

from unittest import mock

from app.dto import product_categories as dto_product_categories
from app.dto.exceptions import common as exceptions_common, product_categories as exceptions_product_categories
from app.db import utils as db_utils, keys_structure as db_keys_structure, common as db_common, s3_key_structure
from conftest import TEST_USER_UUID, insert_product_category_default


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_create_product_category(_mock_upload_file_to_s3, test_client, request):
    owner_uuid = str(uuid.uuid4())
    shop_uuid = str(uuid.uuid4())

    data = dto_product_categories.CategoryCreateRequest(
        title="Test Product Category",
        description="Product Category Description",
        hex_color="FFFFFF",
    )

    url = f'/product_categories/{owner_uuid}/{shop_uuid}'
    file = ('background_img', open("tests/utils/test.svg", "rb"))
    response = test_client.post(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()

    image_url_path = s3_key_structure.product_category_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        file_uuid=uuid.uuid4(),
        image_extention="svg"
    ).rsplit("/", 1)[0]

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': db_keys_structure.product_category_partkey.format(shop_uuid=shop_uuid),
            'sortkey': db_keys_structure.product_category_sortkey.format(uuid=response_body['uuid'])
        })

    request.addfinalizer(resource_teardown)

    assert response_body["uuid"]
    assert response_body["user_uuid"] == TEST_USER_UUID
    assert response_body["owner_uuid"] == owner_uuid
    assert response_body["shop_uuid"] == shop_uuid
    assert response_body["title"] == data.title
    assert response_body["description"] == data.description
    assert response_body["hex_color"] == "white"
    assert image_url_path in response_body["image_url"]
    assert response_body["inactive"] is False
    assert _mock_upload_file_to_s3.call_count == 1


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_product_category(
        _mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_product_category_default, test_client, request):

    owner_uuid = str(insert_product_category_default.owner_uuid)
    shop_uuid = str(insert_product_category_default.shop_uuid)
    category_uuid = str(insert_product_category_default.uuid_)

    data = dto_product_categories.CategoryUpdateRequest(
        title="Test Product Category",
        description="Product Category Description",
        hex_color="FFFFFF",
    )

    url = f'/product_categories/{owner_uuid}/{shop_uuid}/{category_uuid}'
    file = ('background_img', open("tests/utils/test.svg", "rb"))
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()

    image_url_path = s3_key_structure.product_category_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        file_uuid=uuid.uuid4(),
        image_extention="svg"
    ).rsplit("/", 1)[0]

    assert response_body["uuid"] == category_uuid
    assert response_body["user_uuid"] == TEST_USER_UUID
    assert response_body["user_uuid"] != str(insert_product_category_default.user_uuid)
    assert response_body["owner_uuid"] == owner_uuid
    assert response_body["shop_uuid"] == shop_uuid
    assert response_body["title"] == data.title
    assert response_body["description"] == data.description
    assert response_body["hex_color"] == "white"
    assert response_body["image_url"] != str(insert_product_category_default.image_url)
    assert image_url_path in response_body["image_url"]
    assert response_body["inactive"] is False
    assert _mock_upload_file_to_s3.call_count == 1
    assert _mock_delete_files_from_s3.call_count == 1


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_product_category_without_image(_mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_product_category_default, test_client, request):
    owner_uuid = str(insert_product_category_default.owner_uuid)
    shop_uuid = str(insert_product_category_default.shop_uuid)
    category_uuid = str(insert_product_category_default.uuid_)

    data = dto_product_categories.CategoryUpdateRequest(
        title="Test Product Category",
        description="Product Category Description",
        hex_color="FFFFFF",
    )

    url = f'/product_categories/{owner_uuid}/{shop_uuid}/{category_uuid}'
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=None)
    response_body = response.json()

    assert response_body["uuid"] == category_uuid
    assert response_body["user_uuid"] == TEST_USER_UUID
    assert response_body["user_uuid"] != str(insert_product_category_default.user_uuid)
    assert response_body["owner_uuid"] == owner_uuid
    assert response_body["shop_uuid"] == shop_uuid
    assert response_body["title"] == data.title
    assert response_body["description"] == data.description
    assert response_body["hex_color"] == "white"
    assert response_body["image_url"] == str(insert_product_category_default.image_url)
    assert response_body["inactive"] is False
    assert _mock_upload_file_to_s3.call_count == 0
    assert _mock_delete_files_from_s3.call_count == 0


def test_update_product_category_without_image_and_data(insert_product_category_default, test_client, request):
    owner_uuid = str(insert_product_category_default.owner_uuid)
    shop_uuid = str(insert_product_category_default.shop_uuid)
    category_uuid = str(insert_product_category_default.uuid_)

    data = dto_product_categories.CategoryUpdateRequest(
        title=None,
        description=None,
        hex_color=None,
    )

    url = f'/product_categories/{owner_uuid}/{shop_uuid}/{category_uuid}'
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=None)
    response_body = response.json()

    assert response_body == exceptions_common.NoUpdateData.detail
    assert response.status_code == exceptions_common.NoUpdateData.status_code


def test_get_category(insert_product_category_default, test_client, request):
    owner_uuid = str(insert_product_category_default.owner_uuid)
    shop_uuid = str(insert_product_category_default.shop_uuid)
    category_uuid = str(insert_product_category_default.uuid_)

    url = f'/product_categories/{shop_uuid}/{category_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body["uuid"] == category_uuid
    assert response_body["user_uuid"] == str(insert_product_category_default.user_uuid)
    assert response_body["owner_uuid"] == owner_uuid
    assert response_body["shop_uuid"] == shop_uuid
    assert response_body["title"] == insert_product_category_default.title
    assert response_body["description"] == insert_product_category_default.description
    assert response_body["hex_color"] == str(insert_product_category_default.hex_color)
    assert response_body["image_url"] == str(insert_product_category_default.image_url)
    assert response_body["inactive"] is False


def test_get_nonexisten_category(insert_product_category_default, test_client, request):
    shop_uuid = str(insert_product_category_default.shop_uuid)
    category_uuid = str(insert_product_category_default.uuid_)

    url = f'/product_categories/{shop_uuid}/{uuid.uuid4()}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body == exceptions_product_categories.CategoryNotFound.detail
    assert response.status_code == exceptions_product_categories.CategoryNotFound.status_code


def test_get_categories_list(insert_some_product_categories, test_client, request):
    shop_uuid = insert_some_product_categories.category_first.shop_uuid
    url = f'/product_categories/{shop_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()
    category_uuids = [i['uuid'] for i in response_body]

    assert len(response_body) == 2
    assert str(insert_some_product_categories.category_first.uuid_) in category_uuids
    assert str(insert_some_product_categories.category_second.uuid_) in category_uuids
    assert str(insert_some_product_categories.category_inactive.uuid_) not in category_uuids


def test_delete_category(insert_product_category_default, test_client, request):
    owner_uuid = str(insert_product_category_default.owner_uuid)
    shop_uuid = str(insert_product_category_default.shop_uuid)
    category_uuid = str(insert_product_category_default.uuid_)

    url = f'/product_categories/{shop_uuid}/{category_uuid}'
    response = test_client.delete(url=url)

    pk=db_keys_structure.product_category_partkey.format(shop_uuid=shop_uuid)
    sk=db_keys_structure.product_category_sortkey.format(uuid=category_uuid)
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    assert response.status_code == 200
    assert db_item["uuid_"] == category_uuid
    assert db_item["user_uuid"] == TEST_USER_UUID
    assert db_item["owner_uuid"] == owner_uuid
    assert db_item["shop_uuid"] == shop_uuid
    assert db_item["title"] == insert_product_category_default.title
    assert db_item["description"] == insert_product_category_default.description
    assert db_item["hex_color"] == str(insert_product_category_default.hex_color)
    assert db_item["image_url"] == str(insert_product_category_default.image_url)
    assert db_item["inactive"] is True
