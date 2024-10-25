import uuid
from unittest import mock

from app.db import keys_structure as db_keys_structure, common as db_common, utils as db_utils
from app.dto import product_variants as dto_product_variants


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_add_product_variant(_mock_upload_file_to_s3, test_client, request):
    owner_uuid = str(uuid.uuid4())
    shop_uuid = str(uuid.uuid4())
    product_uuid = str(uuid.uuid4())

    url = f'/products/variants/{owner_uuid}/{shop_uuid}/{product_uuid}'
    files = [('images', open("tests/utils/test.svg", "rb")), ('images', open("tests/utils/test.svg", "rb"))]
    option_firts = dto_product_variants.ProductVariantOption(
        title="111",
        article="Option 1",
        price = 100.10,
        weight = 0,
        quantity = 0,
    )
    option_second = dto_product_variants.ProductVariantOption(
        title="222",
        article="Option 2",
        price = 100.10,
        weight = 0,
        quantity = 0,
    )
    request_body = dto_product_variants.ProductVariantCreateRequest(
        title="Test Variant",
        options=[option_firts, option_second]
    )

    response = test_client.post(url=url, data={'data': request_body.model_dump_json()}, files=files)
    response_body = response.json()

    pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=response_body["uuid"]
    )
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    pk_product = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    sk_product = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)
    db_product_item = db_common.get_db_item(partkey=pk_product, sortkey=sk_product)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': pk,
            'sortkey': sk
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': pk_product,
            'sortkey': sk_product
        })

    request.addfinalizer(resource_teardown)

    assert response_body['owner_uuid'] == db_item['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == db_item['shop_uuid'] == shop_uuid
    assert response_body['product_uuid'] == db_item['product_uuid'] == product_uuid
    assert response_body['title'] == db_item['title'] == request_body.title
    assert response_body['options'][0]['title'] == db_item['options'][0]['title'] == request_body.options[0].title
    assert response_body['options'][1]['title'] == db_item['options'][1]['title'] == request_body.options[1].title
    assert float(db_product_item["price"]) == float(response_body['options'][0]['price'])
    assert _mock_upload_file_to_s3.call_count == 2


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_product_variant_minimal_price(
        _mock_upload_file_to_s3, _mock_delete_files_from_s3, test_client, insert_product, request):

    owner_uuid = str(insert_product.product.owner_uuid)
    shop_uuid = str(insert_product.product.shop_uuid)
    product_uuid = str(insert_product.product.product_uuid)
    variant_uuid = str(insert_product.product_variant_first.uuid_)

    url = f'/products/variants/{owner_uuid}/{shop_uuid}/{product_uuid}/{variant_uuid}'
    files = [('images', open("tests/utils/test.svg", "rb")), ('images', open("tests/utils/test.svg", "rb"))]
    option_firts = dto_product_variants.ProductVariantOption(
        title="111",
        article="Option 1",
        price = 3,
        weight = 0,
        quantity = 0,
    )
    option_second = dto_product_variants.ProductVariantOption(
        title="222",
        article="Option 2",
        price = 0,
        weight = 0,
        quantity = 0,
    )
    request_body = dto_product_variants.ProductVariantUpdateRequest(
        title="Test Variant",
        options=[option_firts, option_second],
        image_urls=[str(insert_product.product_variant_first.image_urls[0])]
    )

    response = test_client.patch(url=url, data={'data': request_body.model_dump_json()}, files=files)
    response_body = response.json()

    pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=variant_uuid
    )
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    pk_product = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    sk_product = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)
    db_product_item = db_common.get_db_item(partkey=pk_product, sortkey=sk_product)

    assert response_body['owner_uuid'] == db_item['owner_uuid']
    assert response_body['shop_uuid'] == db_item['shop_uuid']
    assert response_body['product_uuid'] == db_item['product_uuid']
    assert response_body['title'] == db_item['title'] == request_body.title
    assert response_body['options'][0]['title'] == db_item['options'][0]['title']
    assert response_body['options'][0]['title'] != insert_product.product_variant_first.options[0].title
    assert response_body['options'][1]['title'] == db_item['options'][1]['title']
    assert response_body['options'][1]['title'] != insert_product.product_variant_first.options[1].title
    assert len(response_body['image_urls']) == 3
    assert len(db_item['image_urls']) == 3
    assert str(insert_product.product_variant_first.image_urls[0]) in response_body['image_urls']
    assert str(insert_product.product_variant_first.image_urls[1]) not in response_body['image_urls']
    assert float(db_product_item["price"]) == 0
    assert _mock_upload_file_to_s3.call_count == 2
    assert _mock_delete_files_from_s3.call_count == 1


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_product_variant_maximal_price(
        _mock_upload_file_to_s3, _mock_delete_files_from_s3, test_client, insert_product, request):

    owner_uuid = str(insert_product.product.owner_uuid)
    shop_uuid = str(insert_product.product.shop_uuid)
    product_uuid = str(insert_product.product.product_uuid)
    variant_uuid = str(insert_product.product_variant_first.uuid_)

    url = f'/products/variants/{owner_uuid}/{shop_uuid}/{product_uuid}/{variant_uuid}'
    files = [('images', open("tests/utils/test.svg", "rb")), ('images', open("tests/utils/test.svg", "rb"))]
    option_firts = dto_product_variants.ProductVariantOption(
        title="111",
        article="Option 1",
        price = 3000,
        weight = 0,
        quantity = 0,
    )
    option_second = dto_product_variants.ProductVariantOption(
        title="222",
        article="Option 2",
        price = 5000,
        weight = 0,
        quantity = 0,
    )
    request_body = dto_product_variants.ProductVariantUpdateRequest(
        title="Test Variant",
        options=[option_firts, option_second],
        image_urls=[str(insert_product.product_variant_first.image_urls[0])]
    )

    response = test_client.patch(url=url, data={'data': request_body.model_dump_json()}, files=files)
    response_body = response.json()

    pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=variant_uuid
    )
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    pk_product = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    sk_product = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)
    db_product_item = db_common.get_db_item(partkey=pk_product, sortkey=sk_product)

    assert response_body['owner_uuid'] == db_item['owner_uuid']
    assert response_body['shop_uuid'] == db_item['shop_uuid']
    assert response_body['product_uuid'] == db_item['product_uuid']
    assert response_body['title'] == db_item['title'] == request_body.title
    assert response_body['options'][0]['title'] == db_item['options'][0]['title']
    assert response_body['options'][0]['title'] != insert_product.product_variant_first.options[0].title
    assert response_body['options'][1]['title'] == db_item['options'][1]['title']
    assert response_body['options'][1]['title'] != insert_product.product_variant_first.options[1].title
    assert len(response_body['image_urls']) == 3
    assert len(db_item['image_urls']) == 3
    assert str(insert_product.product_variant_first.image_urls[0]) in response_body['image_urls']
    assert str(insert_product.product_variant_first.image_urls[1]) not in response_body['image_urls']
    assert db_product_item["price"] == min([option.price for option in insert_product.product_variant_second.options])
    assert _mock_upload_file_to_s3.call_count == 2
    assert _mock_delete_files_from_s3.call_count == 1


def test_get_product_variant(test_client, insert_product_variant, request):

    owner_uuid = str(insert_product_variant.owner_uuid)
    shop_uuid = str(insert_product_variant.shop_uuid)
    product_uuid = str(insert_product_variant.product_uuid)
    variant_uuid = str(insert_product_variant.uuid_)

    url = f'/products/variants/{owner_uuid}/{shop_uuid}/{product_uuid}/{variant_uuid}/'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body['owner_uuid'] == str(insert_product_variant.owner_uuid)
    assert response_body['shop_uuid'] == str(insert_product_variant.shop_uuid)
    assert response_body['product_uuid'] == str(insert_product_variant.product_uuid)
    assert response_body['uuid'] == str(insert_product_variant.uuid_)
    assert response_body['title'] == insert_product_variant.title
    assert response_body['options'][0]['title'] == insert_product_variant.options[0].title
    assert response_body['options'][1]['title'] == insert_product_variant.options[1].title
    assert response_body['image_urls'] == [str(url) for url in insert_product_variant.image_urls]


def test_get_list_of_product_variants(test_client, insert_some_product_variants, request):

    owner_uuid = str(insert_some_product_variants.variant_active.owner_uuid)
    shop_uuid = str(insert_some_product_variants.variant_active.shop_uuid)
    product_uuid = str(insert_some_product_variants.variant_active.product_uuid)

    url = f'/products/variants/{owner_uuid}/{shop_uuid}/{product_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    uuids = [response_body[0]['uuid'], response_body[1]['uuid']]

    assert len(response_body) == 2
    assert str(insert_some_product_variants.variant_active.uuid_) in uuids
    assert str(insert_some_product_variants.variant_active_second.uuid_) in uuids


def test_delete_product_variant(test_client, insert_product_variant, request):

    owner_uuid = str(insert_product_variant.owner_uuid)
    shop_uuid = str(insert_product_variant.shop_uuid)
    product_uuid = str(insert_product_variant.product_uuid)
    variant_uuid = str(insert_product_variant.uuid_)

    url = f'/products/variants/{owner_uuid}/{shop_uuid}/{product_uuid}/{variant_uuid}/'
    response = test_client.delete(url=url)
    response_body = response.json()

    pk = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=variant_uuid
    )
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    pk_product = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    sk_product = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)
    db_product_item = db_common.get_db_item(partkey=pk_product, sortkey=sk_product)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': pk_product,
            'sortkey': sk_product
        })

    request.addfinalizer(resource_teardown)

    assert db_item['owner_uuid'] == str(insert_product_variant.owner_uuid)
    assert db_item['shop_uuid'] == str(insert_product_variant.shop_uuid)
    assert db_item['product_uuid'] == str(insert_product_variant.product_uuid)
    assert db_item['uuid_'] == str(insert_product_variant.uuid_)
    assert db_item['title'] == insert_product_variant.title
    assert db_item['options'][0]['title'] == insert_product_variant.options[0].title
    assert db_item['options'][1]['title'] == insert_product_variant.options[1].title
    assert db_item['image_urls'] == [str(url) for url in insert_product_variant.image_urls]
    assert db_item['date_update'] != str(insert_product_variant.date_update)
    assert db_item['inactive'] is True
    assert float(db_product_item["price"]) == 0
