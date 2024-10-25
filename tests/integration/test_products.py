import uuid
from unittest import mock

from app.dto import products as dto_products
from app.db import common as db_common, keys_structure as db_keys_structure, utils as db_utils, s3_key_structure
from conftest import TEST_USER_UUID
from app.dto.exceptions import common as exceptions_common
from boto3.dynamodb.conditions import Key, Attr


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_add_product_base_info(_mock_upload_file_to_s3, test_client, request):
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    data = dto_products.ProductBaseInfoCreateRequest(
        title="test template",
        description="test description",
        category_uuids=[
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        ],
    )

    url = f'/products/{owner_uuid}/{shop_uuid}'
    file = ('image', open("tests/utils/test.svg", "rb"))
    response = test_client.post(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()

    product_uuid = response_body["uuid"]
    product_db = db_common.get_db_item(
        partkey=db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid),
        sortkey=db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)
    )

    image_url_path = s3_key_structure.products_base_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        file_uuid=uuid.uuid4(),
        image_extention='svg'
    ).rsplit("/", 1)[0]

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': product_db["partkey"],
            'sortkey': product_db["sortkey"]
        })

    request.addfinalizer(resource_teardown)

    assert bool(product_db)
    assert response_body["user_uuid"] == product_db["user_uuid"] == TEST_USER_UUID
    assert response_body["owner_uuid"] == product_db["owner_uuid"] == str(owner_uuid)
    assert response_body["shop_uuid"] == product_db["shop_uuid"] == str(shop_uuid)
    assert response_body["uuid"] == product_db["uuid_"]
    assert response_body["title"] == product_db["title"] == data.title
    assert response_body["description"] == product_db["description"] == data.description
    assert image_url_path in response_body["image_url"]
    assert image_url_path in product_db["image_url"]
    assert response_body["category_uuids"] == product_db["category_uuids"] == [str(category_uuid) for category_uuid in data.category_uuids]
    assert response_body["date_create"] == product_db["date_create"]
    assert response_body["date_update"] == product_db["date_update"]
    assert product_db["record_type"] == db_keys_structure.product_base_record_type
    assert product_db["inactive"] is False
    assert response_body["inactive"]  is False
    assert _mock_upload_file_to_s3.call_count == 1


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_product_base_info(_mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_product_base_info, test_client, request):
    owner_uuid = insert_product_base_info.owner_uuid
    shop_uuid = insert_product_base_info.shop_uuid
    product_uuid = insert_product_base_info.product_uuid
    data = dto_products.ProductBaseInfoUpdateRequest(
        title="Update Product",
        description="Update Product Description",
        category_uuids=[
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        ],
        inactive = True,
    )

    url = f'/products/{owner_uuid}/{shop_uuid}/{product_uuid}'
    file = ('image', open("tests/utils/test.svg", "rb"))
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()

    product_db = db_common.get_db_item(
        partkey=db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid),
        sortkey=db_keys_structure.product_base_sortkey.format(product_uuid=response_body["uuid"])
    )

    image_url_path = s3_key_structure.products_base_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        file_uuid=uuid.uuid4(),
        image_extention='svg'
    ).rsplit("/", 1)[0]

    assert bool(product_db)
    assert response_body["user_uuid"] == product_db["user_uuid"] == TEST_USER_UUID
    assert response_body["user_uuid"] != str(insert_product_base_info.user_uuid)
    assert response_body["owner_uuid"] == product_db["owner_uuid"] == str(owner_uuid)
    assert response_body["shop_uuid"] == product_db["shop_uuid"] == str(shop_uuid)
    assert response_body["uuid"] == product_db["uuid_"] == str(insert_product_base_info.uuid_)
    assert response_body["title"] == product_db["title"] == data.title
    assert response_body["description"] == product_db["description"] == data.description
    assert response_body["image_url"] == product_db["image_url"]
    assert response_body["image_url"] != str(insert_product_base_info.image_url)
    assert image_url_path in response_body["image_url"]
    assert image_url_path in product_db["image_url"]
    assert response_body["category_uuids"] == product_db["category_uuids"] == [str(category_uuid) for category_uuid in data.category_uuids]
    assert response_body["date_create"] == product_db["date_create"]
    assert response_body["date_update"] != product_db["date_update"]
    assert product_db["record_type"] == db_keys_structure.product_base_record_type
    assert product_db["inactive"] is True
    assert response_body["inactive"]  is True
    assert _mock_upload_file_to_s3.call_count == 1
    assert _mock_delete_files_from_s3.call_count == 1


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_product_base_info_no_data(_mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_product_base_info, test_client, request):
    owner_uuid = insert_product_base_info.owner_uuid
    shop_uuid = insert_product_base_info.shop_uuid
    product_uuid = insert_product_base_info.product_uuid
    data = dto_products.ProductBaseInfoUpdateRequest()

    url = f'/products/{owner_uuid}/{shop_uuid}/{product_uuid}'
    file = ('image', open("tests/utils/test.svg", "rb"))
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()

    product_db = db_common.get_db_item(
        partkey=db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid),
        sortkey=db_keys_structure.product_base_sortkey.format(product_uuid=response_body["uuid"])
    )

    image_url_path = s3_key_structure.products_base_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        file_uuid=uuid.uuid4(),
        image_extention='svg'
    ).rsplit("/", 1)[0]

    assert bool(product_db)
    assert response_body["user_uuid"] == product_db["user_uuid"] == TEST_USER_UUID
    assert response_body["user_uuid"] != str(insert_product_base_info.user_uuid)
    assert response_body["owner_uuid"] == product_db["owner_uuid"] == str(owner_uuid)
    assert response_body["shop_uuid"] == product_db["shop_uuid"] == str(shop_uuid)
    assert response_body["uuid"] == product_db["uuid_"] == str(insert_product_base_info.uuid_)
    assert response_body["title"] == product_db["title"] == insert_product_base_info.title
    assert response_body["description"] == product_db["description"] == insert_product_base_info.description
    assert response_body["image_url"] == product_db["image_url"]
    assert response_body["image_url"] != str(insert_product_base_info.image_url)
    assert image_url_path in response_body["image_url"]
    assert image_url_path in product_db["image_url"]
    assert response_body["category_uuids"] == product_db["category_uuids"] == [str(category_uuid) for category_uuid in insert_product_base_info.category_uuids]
    assert response_body["date_create"] == product_db["date_create"]
    assert response_body["date_update"] != product_db["date_update"]
    assert product_db["record_type"] == db_keys_structure.product_base_record_type
    assert product_db["inactive"] is False
    assert response_body["inactive"]  is False
    assert _mock_upload_file_to_s3.call_count == 1
    assert _mock_delete_files_from_s3.call_count == 1


def test_update_product_base_info_no_file(insert_product_base_info, test_client, request):
    owner_uuid = insert_product_base_info.owner_uuid
    shop_uuid = insert_product_base_info.shop_uuid
    product_uuid = insert_product_base_info.product_uuid
    data = dto_products.ProductBaseInfoUpdateRequest(
        title="Update Product",
        description="Update Product Description",
        category_uuids=[
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        ],
        inactive = True,
    )

    url = f'/products/{owner_uuid}/{shop_uuid}/{product_uuid}'
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=None)
    response_body = response.json()

    product_db = db_common.get_db_item(
        partkey=db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid),
        sortkey=db_keys_structure.product_base_sortkey.format(product_uuid=response_body["uuid"])
    )

    assert bool(product_db)
    assert response_body["user_uuid"] == product_db["user_uuid"] == TEST_USER_UUID
    assert response_body["user_uuid"] != str(insert_product_base_info.user_uuid)
    assert response_body["owner_uuid"] == product_db["owner_uuid"] == str(owner_uuid)
    assert response_body["shop_uuid"] == product_db["shop_uuid"] == str(shop_uuid)
    assert response_body["uuid"] == product_db["uuid_"] == str(insert_product_base_info.uuid_)
    assert response_body["title"] == product_db["title"] == data.title
    assert response_body["description"] == product_db["description"] == data.description
    assert response_body["image_url"] == product_db["image_url"] == str(insert_product_base_info.image_url)
    assert response_body["category_uuids"] == product_db["category_uuids"] == [str(category_uuid) for category_uuid in data.category_uuids]
    assert response_body["date_create"] == product_db["date_create"]
    assert response_body["date_update"] != product_db["date_update"]
    assert product_db["record_type"] == db_keys_structure.product_base_record_type
    assert product_db["inactive"] is True
    assert response_body["inactive"]  is True


def test_update_product_base_info_no_image_and_data(insert_product_base_info, test_client, request):
    owner_uuid = insert_product_base_info.owner_uuid
    shop_uuid = insert_product_base_info.shop_uuid
    product_uuid = insert_product_base_info.product_uuid
    data = dto_products.ProductBaseInfoUpdateRequest()

    url = f'/products/{owner_uuid}/{shop_uuid}/{product_uuid}'
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=None)
    response_body = response.json()

    assert response_body == exceptions_common.NoUpdateData.detail
    assert response.status_code == exceptions_common.NoUpdateData.status_code


def test_get_product_base_info(insert_product_base_info, test_client, request):
    owner_uuid = insert_product_base_info.owner_uuid
    shop_uuid = insert_product_base_info.shop_uuid
    product_uuid = insert_product_base_info.product_uuid

    url = f'/products/{owner_uuid}/{shop_uuid}/{product_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body["user_uuid"] == str(insert_product_base_info.user_uuid)
    assert response_body["owner_uuid"] == str(insert_product_base_info.owner_uuid)
    assert response_body["shop_uuid"] == str(insert_product_base_info.shop_uuid)
    assert response_body["uuid"] == str(insert_product_base_info.uuid_)
    assert response_body["title"] == insert_product_base_info.title
    assert response_body["description"] == insert_product_base_info.description
    assert response_body["image_url"] == str(insert_product_base_info.image_url)
    assert response_body["category_uuids"] == [str(category_uuid) for category_uuid in insert_product_base_info.category_uuids]
    assert response_body["inactive"] == insert_product_base_info.inactive


def test_get_list_of_product_base_info(insert_some_products, test_client, request):
    owner_uuid = insert_some_products.product_firts.product.owner_uuid
    shop_uuid = insert_some_products.product_firts.product.shop_uuid

    url = f'/products/{owner_uuid}/{shop_uuid}/'
    response = test_client.get(url=url)
    response_body = response.json()
    product_uuids = [
        str(insert_some_products.product_firts.product.uuid_),
        str(insert_some_products.product_second.product.uuid_)
    ]

    assert len(response_body) == 2
    assert response_body[0]["uuid"] in product_uuids
    assert response_body[1]["uuid"] in product_uuids


def test_delete_product(insert_some_products, test_client, request):
    owner_uuid = insert_some_products.product_firts.product.owner_uuid
    shop_uuid = insert_some_products.product_firts.product.shop_uuid
    product_uuid = insert_some_products.product_firts.product.uuid_

    url = f'/products/{owner_uuid}/{shop_uuid}/{product_uuid}'
    response = test_client.delete(url=url)

    pk = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    product_first = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(pk),
        filter_expression=Attr('inactive').eq(True),
        projection_expression='inactive'
    )
    product_second = db_common.query_items_paged(
        key_condition_expression=Key('partkey').eq(pk),
        filter_expression=Attr('inactive').eq(False),
        projection_expression='inactive'
    )


    assert response.status_code == 200
    assert len(product_first) == len(insert_some_products.product_firts.model_fields)
    assert len(product_second) == len(insert_some_products.product_second.model_fields)
    for item in product_first:
        assert item["inactive"] is True
    for item in product_second:
        assert item["inactive"] is False
