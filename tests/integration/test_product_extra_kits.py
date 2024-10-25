import uuid
import json

from app.db import keys_structure as db_keys_structure, common as db_common, utils as db_utils
from app.dto import product_extra_kits as dto_product_extra_kits
from conftest import TEST_USER_UUID


def test_add_product_extra_kit(test_client, request):
    owner_uuid = str(uuid.uuid4())
    shop_uuid = str(uuid.uuid4())
    product_uuid = str(uuid.uuid4())

    url = f'/products/extra_kits/{owner_uuid}/{shop_uuid}/{product_uuid}'
    request_body = dto_product_extra_kits.ProductExtraKitCreateRequest(
        title="Test Extra Kit",
        price=100.10,
        addons=[
        "Test",
        "Testik"
        ]
    )

    response = test_client.post(url=url, data=json.dumps(request_body.model_dump_json()))
    response_body = response.json()

    pk = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_extra_kits_sortkey.format(
        product_uuid=product_uuid, extra_kit_uuid=response_body["uuid"]
    )
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
    assert response_body['product_uuid'] == db_item['product_uuid'] == product_uuid
    assert response_body['title'] == db_item['title'] == request_body.title
    assert float(response_body['price']) == float(db_item['price']) == float(request_body.price)
    assert response_body['addons'] == db_item['addons'] == request_body.addons
    assert db_item['record_type'] == db_keys_structure.product_extra_kits_record_type
    assert response_body['inactive'] == db_item['inactive'] == False


def test_update_product_extra_kit(insert_product_extra_kit, test_client, request):
    owner_uuid = str(insert_product_extra_kit.owner_uuid)
    shop_uuid = str(insert_product_extra_kit.shop_uuid)
    product_uuid = str(insert_product_extra_kit.product_uuid)
    extra_kit_uuid = str(insert_product_extra_kit.uuid_)

    url = f'/products/extra_kits/{owner_uuid}/{shop_uuid}/{product_uuid}/{extra_kit_uuid}'
    request_body = dto_product_extra_kits.ProductExtraKitUpdateRequest(
        title="Update Test Extra Kit",
        price=200.20,
        addons=[
        "Test",
        "Update Testik"
        ]
    )

    response = test_client.patch(url=url, data=json.dumps(request_body.model_dump_json()))
    response_body = response.json()

    pk = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_extra_kits_sortkey.format(
        product_uuid=product_uuid, extra_kit_uuid=extra_kit_uuid
    )
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    assert response_body['user_uuid'] == db_item['user_uuid'] == TEST_USER_UUID
    assert response_body['owner_uuid'] == db_item['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == db_item['shop_uuid'] == shop_uuid
    assert response_body['product_uuid'] == db_item['product_uuid'] == product_uuid
    assert response_body['uuid'] == db_item['uuid_'] == str(extra_kit_uuid)
    assert response_body['title'] == db_item['title'] == request_body.title
    assert response_body['title'] != insert_product_extra_kit.title
    assert float(response_body['price']) == float(db_item['price']) == float(request_body.price)
    assert float(response_body['price']) != float(insert_product_extra_kit.price)
    assert response_body['addons'] == db_item['addons'] == request_body.addons
    assert response_body['addons'][0] == insert_product_extra_kit.addons[0]
    assert response_body['addons'][1] != insert_product_extra_kit.addons[1]
    assert db_item['record_type'] == insert_product_extra_kit.record_type
    assert response_body['inactive'] == db_item['inactive'] == insert_product_extra_kit.inactive


def test_get_product_extra_kit(insert_product_extra_kit, test_client, request):
    owner_uuid = str(insert_product_extra_kit.owner_uuid)
    shop_uuid = str(insert_product_extra_kit.shop_uuid)
    product_uuid = str(insert_product_extra_kit.product_uuid)
    extra_kit_uuid = str(insert_product_extra_kit.uuid_)

    url = f'/products/extra_kits/{owner_uuid}/{shop_uuid}/{product_uuid}/{extra_kit_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body['owner_uuid'] == str(owner_uuid)
    assert response_body['shop_uuid'] == str(shop_uuid)
    assert response_body['product_uuid'] == str(product_uuid)
    assert response_body['uuid'] == str(extra_kit_uuid)
    assert response_body['title'] == insert_product_extra_kit.title
    assert response_body['price'] == str(insert_product_extra_kit.price)
    assert response_body['addons'] == insert_product_extra_kit.addons
    assert response_body['inactive'] == insert_product_extra_kit.inactive


def test_get_list_of_product_extra_kits(insert_some_product_extra_kits, test_client, request):
    owner_uuid = str(insert_some_product_extra_kits.extra_kit_firts.owner_uuid)
    shop_uuid = str(insert_some_product_extra_kits.extra_kit_firts.shop_uuid)
    product_uuid = str(insert_some_product_extra_kits.extra_kit_firts.product_uuid)

    url = f'/products/extra_kits/{owner_uuid}/{shop_uuid}/{product_uuid}/'
    response = test_client.get(url=url)
    response_body = response.json()
    extra_kit_uuids = [response_body[0]["uuid"], response_body[1]["uuid"]]


    assert len(response_body) == 2
    assert response_body[0]['owner_uuid'] == str(insert_some_product_extra_kits.extra_kit_firts.owner_uuid)
    assert response_body[0]['shop_uuid'] == str(insert_some_product_extra_kits.extra_kit_firts.shop_uuid)
    assert response_body[0]['product_uuid'] == str(insert_some_product_extra_kits.extra_kit_firts.product_uuid)
    assert response_body[1]['owner_uuid'] == str(insert_some_product_extra_kits.extra_kit_second.owner_uuid)
    assert response_body[1]['shop_uuid'] == str(insert_some_product_extra_kits.extra_kit_second.shop_uuid)
    assert response_body[1]['product_uuid'] == str(insert_some_product_extra_kits.extra_kit_second.product_uuid)
    assert str(insert_some_product_extra_kits.extra_kit_firts.uuid_) in extra_kit_uuids
    assert str(insert_some_product_extra_kits.extra_kit_second.uuid_) in extra_kit_uuids
    assert str(insert_some_product_extra_kits.extra_kit_inactive.uuid_) not in extra_kit_uuids


def test_delete_product_extra_kit(test_client, insert_product_extra_kit):
    owner_uuid = str(insert_product_extra_kit.owner_uuid)
    shop_uuid = str(insert_product_extra_kit.shop_uuid)
    product_uuid = str(insert_product_extra_kit.product_uuid)
    extra_kit_uuid = str(insert_product_extra_kit.uuid_)

    url = f'/products/extra_kits/{owner_uuid}/{shop_uuid}/{product_uuid}/{extra_kit_uuid}/'
    response = test_client.delete(url=url)
    response_body = response.json()

    pk = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_extra_kits_sortkey.format(
        product_uuid=product_uuid, extra_kit_uuid=extra_kit_uuid
    )
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    assert db_item['owner_uuid'] == str(owner_uuid)
    assert db_item['shop_uuid'] == str(shop_uuid)
    assert db_item['product_uuid'] == str(product_uuid)
    assert db_item['uuid_'] == str(insert_product_extra_kit.uuid_)
    assert db_item['title'] == insert_product_extra_kit.title
    assert float(db_item['price']) == float(insert_product_extra_kit.price)
    assert db_item['addons'] == insert_product_extra_kit.addons
    assert db_item['date_update'] != str(insert_product_extra_kit.date_update)
    assert db_item['inactive'] == True
