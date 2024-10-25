import uuid

from unittest import mock

from app.dto import infopages_rubrics as dto_infopages_rubrics
from app.dto.exceptions import common as exceptions_common, infopages_rubrics as exceptions_infopages_rubrics
from app.db import utils as db_utils, keys_structure as db_keys_structure, common as db_common, s3_key_structure
from conftest import TEST_USER_UUID


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_create_rubric(_mock_upload_file_to_s3, test_client, request):
    owner_uuid = str(uuid.uuid4())
    shop_uuid = str(uuid.uuid4())

    data = dto_infopages_rubrics.RubricCreateRequest(
        title="Test Rubric",
        description="Test Rubric Description",
        hex_color="FFFFFF",
    )

    url = f'/infopages/rubrics/{owner_uuid}/{shop_uuid}'
    file = ('image', open("tests/utils/test.svg", "rb"))
    response = test_client.post(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()
    image_url_path = s3_key_structure.infopages_rubric_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        file_uuid=uuid.uuid4(),
        image_extention="svg"
    ).rsplit("/", 1)[0]

    pk = db_keys_structure.infopages_rubrics_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.infopages_rubrics_sortkey.format(rubric_uuid=response_body['uuid'])
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': pk,
            'sortkey': sk
        })

    request.addfinalizer(resource_teardown)

    assert response_body["uuid"] == db_item["uuid_"]
    assert response_body["user_uuid"] == db_item["user_uuid"] == TEST_USER_UUID
    assert response_body["owner_uuid"] == db_item["owner_uuid"] == owner_uuid
    assert response_body["shop_uuid"] == db_item["shop_uuid"] == shop_uuid
    assert response_body["title"] == db_item["title"] == data.title
    assert response_body["description"] == db_item["description"] == data.description
    assert response_body["hex_color"] == db_item["hex_color"] == "white"
    assert response_body["image_url"] == db_item["image_url"]
    assert image_url_path in response_body["image_url"]
    assert image_url_path in db_item["image_url"]
    assert response_body["inactive"] is False
    assert db_item["inactive"] is False
    assert _mock_upload_file_to_s3.call_count == 1


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_rubric(_mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_infopages_rubric, test_client, request):
    owner_uuid = str(insert_infopages_rubric.owner_uuid)
    shop_uuid = str(insert_infopages_rubric.shop_uuid)
    rubric_uuid = str(insert_infopages_rubric.uuid_)

    data = dto_infopages_rubrics.RubricUpdateRequest(
        title="Test Infopages Rubric",
        description="Update Infopages Rubric Description",
        hex_color="FFFFFF",
    )

    url = f'/infopages/rubrics/{owner_uuid}/{shop_uuid}/{rubric_uuid}'
    file = ('image', open("tests/utils/test.svg", "rb"))
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=[file])
    response_body = response.json()

    image_url_path = s3_key_structure.infopages_rubric_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        file_uuid=uuid.uuid4(),
        image_extention="svg"
    ).rsplit("/", 1)[0]

    assert response_body["uuid"] == rubric_uuid
    assert response_body["user_uuid"] == TEST_USER_UUID
    assert response_body["user_uuid"] != str(insert_infopages_rubric.user_uuid)
    assert response_body["owner_uuid"] == owner_uuid
    assert response_body["shop_uuid"] == shop_uuid
    assert response_body["title"] == data.title
    assert response_body["description"] == data.description
    assert response_body["hex_color"] == "white"
    assert response_body["image_url"] != str(insert_infopages_rubric.image_url)
    assert image_url_path in response_body["image_url"]
    assert response_body["inactive"] is False
    assert _mock_upload_file_to_s3.call_count == 1
    assert _mock_delete_files_from_s3.call_count == 1


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_rubric_without_image(_mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_infopages_rubric, test_client, request):
    owner_uuid = str(insert_infopages_rubric.owner_uuid)
    shop_uuid = str(insert_infopages_rubric.shop_uuid)
    rubric_uuid = str(insert_infopages_rubric.uuid_)

    data = dto_infopages_rubrics.RubricUpdateRequest(
        title="Test Infopages Rubric",
        description="Update Infopages Rubric Description",
        hex_color="FFFFFF",
    )

    url = f'/infopages/rubrics/{owner_uuid}/{shop_uuid}/{rubric_uuid}'
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=None)
    response_body = response.json()

    assert response_body["uuid"] == rubric_uuid
    assert response_body["user_uuid"] == TEST_USER_UUID
    assert response_body["user_uuid"] != str(insert_infopages_rubric.user_uuid)
    assert response_body["owner_uuid"] == owner_uuid
    assert response_body["shop_uuid"] == shop_uuid
    assert response_body["title"] == data.title
    assert response_body["description"] == data.description
    assert response_body["hex_color"] == "white"
    assert response_body["image_url"] == str(insert_infopages_rubric.image_url)
    assert response_body["inactive"] is False
    assert _mock_upload_file_to_s3.call_count == 0
    assert _mock_delete_files_from_s3.call_count == 0


def test_update_rubric_without_image_and_data(insert_infopages_rubric, test_client, request):
    owner_uuid = str(insert_infopages_rubric.owner_uuid)
    shop_uuid = str(insert_infopages_rubric.shop_uuid)
    rubric_uuid = str(insert_infopages_rubric.uuid_)

    data = dto_infopages_rubrics.RubricUpdateRequest(
        title=None,
        description=None,
        hex_color=None,
    )

    url = f'/infopages/rubrics/{owner_uuid}/{shop_uuid}/{rubric_uuid}'
    response = test_client.patch(url=url, data={'data': data.model_dump_json()}, files=None)
    response_body = response.json()

    assert response_body == exceptions_common.NoUpdateData.detail
    assert response.status_code == exceptions_common.NoUpdateData.status_code


def test_get_rubric(insert_infopages_rubric, test_client, request):
    shop_uuid = str(insert_infopages_rubric.shop_uuid)
    rubric_uuid = str(insert_infopages_rubric.uuid_)

    url = f'/infopages/rubrics/{shop_uuid}/{rubric_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body["uuid"] == str(insert_infopages_rubric.uuid_)
    assert response_body["user_uuid"] == str(insert_infopages_rubric.user_uuid)
    assert response_body["owner_uuid"] == str(insert_infopages_rubric.owner_uuid)
    assert response_body["shop_uuid"] == str(insert_infopages_rubric.shop_uuid)
    assert response_body["title"] == insert_infopages_rubric.title
    assert response_body["description"] == insert_infopages_rubric.description
    assert response_body["hex_color"] == "white"
    assert response_body["image_url"] == str(insert_infopages_rubric.image_url)
    assert response_body["inactive"] is False


def test_get_nonexisten_rubric(insert_infopages_rubric, test_client, request):
    shop_uuid = str(insert_infopages_rubric.shop_uuid)

    url = f'/infopages/rubrics/{shop_uuid}/{uuid.uuid4()}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body == exceptions_infopages_rubrics.RubricNotFound.detail
    assert response.status_code == exceptions_infopages_rubrics.RubricNotFound.status_code


def test_get_list_of_rubrics(insert_some_infopages_rubrics, test_client, request):
    shop_uuid = insert_some_infopages_rubrics.rubric_first.shop_uuid
    url = f'/infopages/rubrics/{shop_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()
    rubric_uuids = [r["uuid"] for r in response_body]

    assert len(response_body) == 2
    assert str(insert_some_infopages_rubrics.rubric_first.uuid_) in rubric_uuids
    assert str(insert_some_infopages_rubrics.rubric_second.uuid_) in rubric_uuids


def test_delete_rubric(insert_infopages_rubric, test_client, request):
    owner_uuid = str(insert_infopages_rubric.owner_uuid)
    shop_uuid = str(insert_infopages_rubric.shop_uuid)
    rubric_uuid = str(insert_infopages_rubric.uuid_)

    url = f'/infopages/rubrics/{shop_uuid}/{rubric_uuid}'
    response = test_client.delete(url=url)

    pk=db_keys_structure.infopages_rubrics_partkey.format(shop_uuid=shop_uuid)
    sk=db_keys_structure.infopages_rubrics_sortkey.format(rubric_uuid=rubric_uuid)
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    assert response.status_code == 200
    assert db_item["uuid_"] == rubric_uuid
    assert db_item["user_uuid"] == TEST_USER_UUID
    assert db_item["owner_uuid"] == owner_uuid
    assert db_item["shop_uuid"] == shop_uuid
    assert db_item["title"] == insert_infopages_rubric.title
    assert db_item["description"] == insert_infopages_rubric.description
    assert db_item["hex_color"] == str(insert_infopages_rubric.hex_color)
    assert db_item["image_url"] == str(insert_infopages_rubric.image_url)
    assert db_item["inactive"] is True
