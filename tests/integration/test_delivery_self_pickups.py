import uuid
import json

from app.db import keys_structure as db_keys_structure, common as db_common, utils as db_utils
from app.dto import delivery_self_pickup as dto_delivery_self_pickup
from conftest import TEST_USER_UUID, TEST_USER, TEST_PHONE, generate_test_schedule


def test_add_delivery_self_pickup(test_client, request):
    owner_uuid = str(uuid.uuid4())
    shop_uuid = str(uuid.uuid4())

    url = f'/delivery/self_pickup/{owner_uuid}/{shop_uuid}'
    request_body = dto_delivery_self_pickup.DeliverySelfPickupCreateRequest(
        title="Test Delivery Self Pickup",
        description="Test Delivery Self Pickup Description",
        contact_phone=TEST_PHONE,
        schedule=generate_test_schedule(),
    )

    response = test_client.post(url=url, data=json.dumps(request_body.model_dump_json()))
    response_body = response.json()

    pk = db_keys_structure.delivery_self_pickup_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.delivery_self_pickup_sortkey.format(self_pickup_uuid=response_body["uuid"])
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
    assert response_body['schedule'] == request_body.schedule.model_dump()
    assert db_item['schedule'] == request_body.schedule.model_dump(exclude_none=True)
    assert db_item['record_type'] == db_keys_structure.delivery_self_pickup_record_type
    assert response_body['inactive'] == db_item['inactive'] == False


def test_update_delivery_self_pickup(insert_delivery_self_pickup, test_client, request):
    owner_uuid = str(insert_delivery_self_pickup.owner_uuid)
    shop_uuid = str(insert_delivery_self_pickup.shop_uuid)
    self_pickup_uuid = str(insert_delivery_self_pickup.uuid_)

    url = f'/delivery/self_pickup/{owner_uuid}/{shop_uuid}/{self_pickup_uuid}'
    schedule = generate_test_schedule()
    schedule.thursday.time_stop = "16:00:00"
    schedule.friday = None
    request_body = dto_delivery_self_pickup.DeliverySelfPickupCreateRequest(
        title="Update Test Delivery Self Pickup",
        description="Update Test Delivery Self Pickup Description",
        contact_phone=TEST_PHONE,
        contact_tg_username=TEST_USER.tg_username,
        schedule=schedule,
    )

    response = test_client.patch(url=url, data=json.dumps(request_body.model_dump_json()))
    response_body = response.json()

    assert response_body['user_uuid'] == TEST_USER_UUID
    assert response_body['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == shop_uuid
    assert response_body['uuid'] == self_pickup_uuid
    assert response_body['title'] == request_body.title
    assert response_body['description'] == request_body.description
    assert response_body['contact_phone'] == request_body.contact_phone
    assert response_body['contact_tg_username'] == request_body.contact_tg_username
    assert response_body['schedule']["monday"] == insert_delivery_self_pickup.schedule.monday.model_dump()
    assert response_body['schedule']["tuesday"] == insert_delivery_self_pickup.schedule.tuesday.model_dump()
    assert response_body['schedule']["wednesday"] == insert_delivery_self_pickup.schedule.wednesday.model_dump()
    assert response_body['schedule']["thursday"] == request_body.schedule.thursday.model_dump()
    assert response_body['schedule'].get("friday", False) is None
    assert response_body['schedule'].get("saturday", False) is None
    assert response_body['schedule'].get("sunday", False) is None
    assert response_body['inactive'] is False


def test_update_delivery_self_pickup_no_schedule(insert_delivery_self_pickup, test_client, request):
    owner_uuid = str(insert_delivery_self_pickup.owner_uuid)
    shop_uuid = str(insert_delivery_self_pickup.shop_uuid)
    self_pickup_uuid = str(insert_delivery_self_pickup.uuid_)

    url = f'/delivery/self_pickup/{owner_uuid}/{shop_uuid}/{self_pickup_uuid}'
    request_body = dto_delivery_self_pickup.DeliverySelfPickupCreateRequest(
        title="Update Test Delivery Self Pickup",
        description="Update Test Delivery Self Pickup Description",
        contact_phone=TEST_PHONE,
        contact_tg_username=TEST_USER.tg_username,
        schedule=None,
    )

    response = test_client.patch(url=url, data=json.dumps(request_body.model_dump_json()))
    response_body = response.json()

    assert response_body['user_uuid'] == TEST_USER_UUID
    assert response_body['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == shop_uuid
    assert response_body['uuid'] == self_pickup_uuid
    assert response_body['title'] == request_body.title
    assert response_body['description'] == request_body.description
    assert response_body['contact_phone'] == request_body.contact_phone
    assert response_body['contact_tg_username'] == request_body.contact_tg_username
    assert response_body['schedule'] == insert_delivery_self_pickup.schedule.model_dump()
    assert response_body['inactive'] is False


def test_get_delivery_self_pickup(insert_delivery_self_pickup, test_client, request):
    owner_uuid = str(insert_delivery_self_pickup.owner_uuid)
    shop_uuid = str(insert_delivery_self_pickup.shop_uuid)
    self_pickup_uuid = str(insert_delivery_self_pickup.uuid_)

    url = f'/delivery/self_pickup/{owner_uuid}/{shop_uuid}/{self_pickup_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body['user_uuid'] == str(insert_delivery_self_pickup.user_uuid)
    assert response_body['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == shop_uuid
    assert response_body['uuid'] == str(insert_delivery_self_pickup.uuid_)
    assert response_body['title'] == insert_delivery_self_pickup.title
    assert response_body['description'] == insert_delivery_self_pickup.description
    assert response_body['contact_phone'] == insert_delivery_self_pickup.contact_phone
    assert response_body['contact_tg_username'] == insert_delivery_self_pickup.contact_tg_username
    assert response_body['schedule'] == insert_delivery_self_pickup.schedule.model_dump()
    assert response_body['inactive'] == insert_delivery_self_pickup.inactive


def test_get_list_of_delivery_self_pickup(insert_some_delivery_self_pickup, test_client, request):
    owner_uuid = str(insert_some_delivery_self_pickup.self_pickup_first.owner_uuid)
    shop_uuid = str(insert_some_delivery_self_pickup.self_pickup_first.shop_uuid)

    url = f'/delivery/self_pickup/{owner_uuid}/{shop_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    self_pickup_uuids = [r["uuid"] for r in response_body]

    assert len(response_body) == 2
    assert str(insert_some_delivery_self_pickup.self_pickup_first.uuid_) in self_pickup_uuids
    assert str(insert_some_delivery_self_pickup.self_pickup_second.uuid_) in self_pickup_uuids


def test_delete_delivery_self_pickup(insert_delivery_self_pickup, test_client, request):
    owner_uuid = str(insert_delivery_self_pickup.owner_uuid)
    shop_uuid = str(insert_delivery_self_pickup.shop_uuid)
    self_pickup_uuid = str(insert_delivery_self_pickup.uuid_)

    url = f'/delivery/self_pickup/{owner_uuid}/{shop_uuid}/{self_pickup_uuid}'
    response = test_client.delete(url=url)

    pk = db_keys_structure.delivery_self_pickup_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.delivery_self_pickup_sortkey.format(self_pickup_uuid=self_pickup_uuid)
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    assert response.status_code == 200
    assert db_item['user_uuid'] == TEST_USER_UUID
    assert db_item['owner_uuid'] == owner_uuid
    assert db_item['shop_uuid'] == shop_uuid
    assert db_item['uuid_'] == str(insert_delivery_self_pickup.uuid_)
    assert db_item['title'] == insert_delivery_self_pickup.title
    assert db_item['description'] == insert_delivery_self_pickup.description
    assert db_item['contact_phone'] == insert_delivery_self_pickup.contact_phone
    assert db_item['contact_tg_username'] == insert_delivery_self_pickup.contact_tg_username
    assert db_item['schedule'] == insert_delivery_self_pickup.schedule.model_dump(exclude_none=True)
    assert db_item['inactive'] is True
