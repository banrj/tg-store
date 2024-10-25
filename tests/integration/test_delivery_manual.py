import uuid
import json

from app.db import keys_structure as db_keys_structure, common as db_common, utils as db_utils
from app.dto import delivery_manual as dto_delivery_manual
from conftest import TEST_USER_UUID, TEST_USER, TEST_PHONE, generate_test_schedule


def test_add_delivery_manual(test_client, request):
    owner_uuid = str(uuid.uuid4())
    shop_uuid = str(uuid.uuid4())

    url = f'/delivery/manual/{owner_uuid}/{shop_uuid}'
    request_body = dto_delivery_manual.DeliveryManualCreateRequest(
        title="Test Delivery Manual",
        description="Test Delivery Manual Description",
        contact_phone=TEST_PHONE,
        price=100.1
    )

    response = test_client.post(url=url, data=json.dumps(request_body.model_dump_json()))
    response_body = response.json()

    pk = db_keys_structure.delivery_manual_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.delivery_manual_sortkey.format(delivery_manual_uuid=response_body["uuid"])
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': pk,
            'sortkey': sk
        })

    request.addfinalizer(resource_teardown)

    assert response_body['user_uuid'] == db_item['user_uuid'] == TEST_USER_UUID
    assert response_body['owner_uuid'] == db_item['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == db_item['shop_uuid'] == shop_uuid
    assert response_body['uuid'] == db_item['uuid_']
    assert response_body['title'] == db_item['title'] == request_body.title
    assert response_body['description'] == db_item['description'] == request_body.description
    assert response_body['contact_phone'] == db_item['contact_phone'] == request_body.contact_phone
    assert response_body['contact_tg_username'] == db_item['contact_tg_username'] == TEST_USER.tg_username
    assert float(response_body['price']) == float(request_body.price)
    assert db_item['record_type'] == db_keys_structure.delivery_manual_record_type
    assert response_body['inactive'] == db_item['inactive'] == False


def test_update_delivery_manual(insert_delivery_manual, test_client, request):
    owner_uuid = str(insert_delivery_manual.owner_uuid)
    shop_uuid = str(insert_delivery_manual.shop_uuid)
    delivery_manual_uuid = str(insert_delivery_manual.uuid_)

    url = f'/delivery/manual/{owner_uuid}/{shop_uuid}/{delivery_manual_uuid}'
    request_body = dto_delivery_manual.DeliveryManualUpdateRequest(
        title="Update Test Delivery Manual",
        description="Update Test Delivery Manual Description",
        contact_phone=TEST_PHONE,
        price=200.2,
    )

    response = test_client.patch(url=url, data=json.dumps(request_body.model_dump_json()))
    response_body = response.json()

    assert response_body['user_uuid'] == TEST_USER_UUID
    assert response_body['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == shop_uuid
    assert response_body['uuid'] == delivery_manual_uuid
    assert response_body['title'] == request_body.title
    assert response_body['description'] == request_body.description
    assert response_body['contact_phone'] == request_body.contact_phone
    assert response_body['contact_tg_username'] == insert_delivery_manual.contact_tg_username
    assert float(response_body['price']) == float(request_body.price)
    assert response_body['inactive'] is False


def test_get_delivery_manual(insert_delivery_manual, test_client, request):
    owner_uuid = str(insert_delivery_manual.owner_uuid)
    shop_uuid = str(insert_delivery_manual.shop_uuid)
    delivery_manual_uuid = str(insert_delivery_manual.uuid_)

    url = f'/delivery/manual/{owner_uuid}/{shop_uuid}/{delivery_manual_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body['user_uuid'] == str(insert_delivery_manual.user_uuid)
    assert response_body['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == shop_uuid
    assert response_body['uuid'] == str(insert_delivery_manual.uuid_)
    assert response_body['title'] == insert_delivery_manual.title
    assert response_body['description'] == insert_delivery_manual.description
    assert response_body['contact_phone'] == insert_delivery_manual.contact_phone
    assert response_body['contact_tg_username'] == insert_delivery_manual.contact_tg_username
    assert float(response_body['price']) == float(insert_delivery_manual.price)
    assert response_body['inactive'] == insert_delivery_manual.inactive


def test_get_list_of_delivery_manuals(insert_some_delivery_manual, test_client, request):
    owner_uuid = str(insert_some_delivery_manual.delivery_manual_first.owner_uuid)
    shop_uuid = str(insert_some_delivery_manual.delivery_manual_first.shop_uuid)

    url = f'/delivery/manual/{owner_uuid}/{shop_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    delivery_manual_uuids = [r["uuid"] for r in response_body]

    assert len(response_body) == 2
    assert str(insert_some_delivery_manual.delivery_manual_first.uuid_) in delivery_manual_uuids
    assert str(insert_some_delivery_manual.delivery_manual_second.uuid_) in delivery_manual_uuids


def test_delete_delivery_manual(insert_delivery_manual, test_client, request):
    owner_uuid = str(insert_delivery_manual.owner_uuid)
    shop_uuid = str(insert_delivery_manual.shop_uuid)
    delivery_manual_uuid = str(insert_delivery_manual.uuid_)

    url = f'/delivery/manual/{owner_uuid}/{shop_uuid}/{delivery_manual_uuid}'
    response = test_client.delete(url=url)

    pk = db_keys_structure.delivery_manual_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.delivery_manual_sortkey.format(delivery_manual_uuid=delivery_manual_uuid)
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    assert response.status_code == 200
    assert db_item['user_uuid'] == TEST_USER_UUID
    assert db_item['owner_uuid'] == owner_uuid
    assert db_item['shop_uuid'] == shop_uuid
    assert db_item['uuid_'] == str(insert_delivery_manual.uuid_)
    assert db_item['title'] == insert_delivery_manual.title
    assert db_item['description'] == insert_delivery_manual.description
    assert db_item['contact_phone'] == insert_delivery_manual.contact_phone
    assert db_item['contact_tg_username'] == insert_delivery_manual.contact_tg_username
    assert float(db_item['price']) == float(insert_delivery_manual.price)
    assert db_item['inactive'] is True
