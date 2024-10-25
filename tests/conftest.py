import uuid
import datetime
from collections import namedtuple

import pydantic
import pytest
import random
import string

from fastapi.testclient import TestClient

import utils as test_utils
from app.db import (
    utils as db_utils,
    keys_structure as db_keys_structure,
    s3_key_structure
)
from app import settings
from app.dto import (
    user as dto_user,
    shop as dto_shop,
    template as dto_template,
    products as dto_products,
    product_variants as dto_product_variants,
    product_categories as dto_product_categories,
    product_extra_kits as dto_product_extra_kits,
    delivery_self_pickup as dto_delivery_self_pickup,
    delivery_manual as dto_delivery_manual,
    infopages_rubrics as dto_infopages_rubrics,
    infopages_posts as dto_infopages_posts,
)
from app.handlers import shop as shop_handlers
from app.main import app
from app.handlers import auth as handlers_auth

db_utils.init_local_db_test_table(table_suffix=settings.TABLE_SUFFIX)


TEST_USER_UUID = '00000000-0000-4000-8000-000000000000'
TEST_PHONE = "+79062000000"
TEST_USER = dto_user.User(
    uuid=TEST_USER_UUID,
    user_uuid=TEST_USER_UUID,
    tg_id=1,
    tg_first_name="first_name",
    tg_last_name="last_name",
    tg_username="tg_username",
    tg_photo_url='http://www.example.com',
    tg_auth_date=100,
    email='noreply@google.com',
    record_type=db_keys_structure.user_record_type,
)


@pytest.fixture(scope='function')
def tables_connection(request) -> db_utils.SetupTablesConnection:
    request.addfinalizer(test_utils.drop_general_table)
    request.addfinalizer(test_utils.drop_tokens_table)

    return db_utils.SetupTablesConnection()()


@pytest.fixture(scope="function")
def test_client():
    """
    Создаем тестовый клиент для тестирования запросов.
    """

    def override_auth_data():
        return dto_user.AuthData(user=TEST_USER)

    with TestClient(app) as test_client:
        app.dependency_overrides[handlers_auth.auth_user] = override_auth_data
        yield test_client


@pytest.fixture(scope='function')
def insert_user(request):
    tg_id = 1
    first_name = 'first_name'
    last_name = 'last_name'
    username = 'username'
    auth_date = 100
    photo_url = 'http://www.example.com'
    tg_hash = 'tg_hash'
    user_tg_item = dto_user.TgUser(
        id_=tg_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        photo_url=photo_url,
        auth_date=auth_date,
        user_uuid=uuid.uuid4(),
        date_create=datetime.datetime.now(),
        record_type=db_keys_structure.tg_user_record_type,
    )
    user_tg_item._partkey=db_keys_structure.tg_user_partkey
    user_tg_item._sortkey=db_keys_structure.tg_user_sortkey.format(tg_id=tg_id)

    user_item = dto_user.User(
        uuid=user_tg_item.user_uuid,
        user_uuid=user_tg_item.user_uuid,
        tg_id=user_tg_item.id_,
        tg_first_name=user_tg_item.first_name,
        tg_last_name=user_tg_item.last_name,
        tg_username=user_tg_item.username,
        tg_photo_url=user_tg_item.photo_url,
        tg_auth_date=user_tg_item.auth_date,
        email='noreply@google.com',
        record_type = db_keys_structure.user_record_type,
    )
    user_item._partkey = db_keys_structure.user_partkey
    user_item._sortkey = db_keys_structure.user_sortkey.format(uuid=user_tg_item.user_uuid)

    db_utils.get_gen_table().put_item(Item=user_tg_item.to_record())
    db_utils.get_gen_table().put_item(Item=user_item.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': user_tg_item._partkey,
            'sortkey': user_tg_item._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': user_item._partkey,
            'sortkey': user_item._sortkey
        })

    request.addfinalizer(resource_teardown)

    return user_tg_item, user_item


def get_logo_url(shop_uuid):
    bucket_url = s3_key_structure.shop_file_path.format(shop_uuid=str(shop_uuid), file_uuid=uuid.uuid4(), photo_extention="svg")
    return s3_key_structure.shop_logo_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_SERVICE_BUCKET_NAME,
        file_name=bucket_url
    )


def put_shop_to_db(owner_uuid, template_uuid, inactive=True, subscription_active=True,
                   subscription_expire_at=shop_handlers.trial_period_for_new_shop()):
    shop_uuid = uuid.uuid4()
    shop_payload = dto_shop.Shop(
        uuid_=shop_uuid,
        user_uuid=owner_uuid,
        owner_uuid=owner_uuid,
        title='test shop',
        description='test description',
        subscription_active=subscription_active,
        subscription_expire_at=subscription_expire_at,
        template_uuid=template_uuid,
        shop_type=dto_shop.ShopTypes.online_store.value,
        inactive=inactive,
        logo_url=get_logo_url(shop_uuid),
        record_type=db_keys_structure.shop_record_type,
    )
    shop_payload._partkey = db_keys_structure.shop_partkey
    shop_payload._sortkey = db_keys_structure.shop_sortkey.format(shop_uuid=shop_uuid)
    db_utils.get_gen_table().put_item(Item=shop_payload.to_record())
    return shop_payload


@pytest.fixture(scope='function')
def insert_inactive_shop(request):
    owner_uuid = uuid.uuid4()
    template_uuid = uuid.uuid4()
    shop_payload = put_shop_to_db(owner_uuid, template_uuid)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': shop_payload._partkey,
            'sortkey': shop_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return shop_payload


@pytest.fixture(scope='function')
def insert_active_shop(request):
    owner_uuid = uuid.uuid4()
    template_uuid = uuid.uuid4()
    shop_payload = put_shop_to_db(owner_uuid, template_uuid, inactive=False)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': shop_payload._partkey,
            'sortkey': shop_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return shop_payload


@pytest.fixture(scope='function')
def insert_shop_same_owner_and_user(request):
    owner_uuid = TEST_USER_UUID
    template_uuid = uuid.uuid4()
    shop_payload = put_shop_to_db(owner_uuid, template_uuid, inactive=False)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': shop_payload._partkey,
            'sortkey': shop_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return shop_payload


@pytest.fixture(scope='function')
def insert_some_shops(request):
    owner_uuid = uuid.uuid4()
    template_uuid = uuid.uuid4()
    shop_first = put_shop_to_db(owner_uuid, template_uuid, inactive=False)
    shop_second = put_shop_to_db(owner_uuid, template_uuid, inactive=False)
    shop_inactive = put_shop_to_db(owner_uuid, template_uuid, inactive=True)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': shop_first._partkey,
            'sortkey': shop_first._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': shop_second._partkey,
            'sortkey': shop_second._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': shop_inactive._partkey,
            'sortkey': shop_inactive._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "shop_first, shop_second, shop_inactive")(shop_first, shop_second, shop_inactive)


def get_template_photo_url(template_uuid):
    bucket_url = s3_key_structure.template_file_path.format(template_uuid=str(template_uuid), photo_extention="svg")
    return s3_key_structure.template_photo_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_SERVICE_BUCKET_NAME,
        file_name=bucket_url
    )


@pytest.fixture(scope='function')
def insert_active_template(request):
    template_uuid = uuid.uuid4()

    template_payload = dto_template.Template(
        uuid_ = template_uuid,
        title = "active template",
        description = "active template description",
        photo_url = get_template_photo_url(template_uuid),
        template_url = "https://fake.com/",
        exclusive_owner_uuid = None,
        date_create = datetime.datetime.now().isoformat(),
        record_type = db_keys_structure.template_record_type,
    )
    template_payload._partkey = template_payload._partkey
    template_payload._sortkey = template_payload._sortkey.format(uuid=template_uuid)
    db_utils.get_gen_table().put_item(Item=template_payload.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': template_payload._partkey,
            'sortkey': template_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return template_payload


@pytest.fixture(scope='function')
def insert_inactive_template(request):
    template_uuid = uuid.uuid4()

    template_payload = dto_template.Template(
        uuid_ = template_uuid,
        title = "inactive template",
        description = "inactive template description",
        photo_url = get_template_photo_url(template_uuid),
        template_url = "https://fake.com/",
        exclusive_owner_uuid = None,
        date_create = datetime.datetime.now().isoformat(),
        inactive = True,
        record_type=db_keys_structure.template_record_type,
    )
    template_payload._partkey = template_payload._partkey
    template_payload._sortkey = template_payload._sortkey.format(uuid=template_uuid)
    db_utils.get_gen_table().put_item(Item=template_payload.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': template_payload._partkey,
            'sortkey': template_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return template_payload


def get_product_category_image_url(shop_uuid, owner_uuid, category_uuid):
    bucket_url = s3_key_structure.product_category_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        file_uuid=uuid.uuid4(),
        image_extention="svg"
    )
    return s3_key_structure.product_category_image_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
        file_name=bucket_url
    )


def put_category_to_db(owner_uuid, shop_uuid, user_uuid, sort_index=1, inactive=False):
    category_uuid = uuid.uuid4()
    image_url = get_product_category_image_url(shop_uuid=shop_uuid, owner_uuid=owner_uuid, category_uuid=category_uuid)
    category_payload = dto_product_categories.Category(
        uuid_=category_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        title="Test Default Category",
        description="Test Default Category Description",
        inactive=inactive,
        date_create=datetime.datetime.now().isoformat(),
        hex_color="AFAFAF",
        image_url=image_url,
        sort_index=sort_index,
        record_type=db_keys_structure.product_category_record_type,
    )
    category_payload._partkey = db_keys_structure.product_category_partkey.format(shop_uuid=shop_uuid)
    category_payload._sortkey = db_keys_structure.product_category_sortkey.format(uuid=category_uuid)
    db_utils.get_gen_table().put_item(Item=category_payload.to_record())
    return category_payload


@pytest.fixture(scope='function')
def insert_product_category_default(request):
    owner_uuid = uuid.uuid4()
    user_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    category_payload = put_category_to_db(owner_uuid, shop_uuid, user_uuid, sort_index=0)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': category_payload._partkey,
            'sortkey': category_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return category_payload


@pytest.fixture(scope='function')
def insert_product_category(request):
    owner_uuid = uuid.uuid4()
    user_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()

    category_payload = put_category_to_db(owner_uuid, shop_uuid, user_uuid, sort_index=3)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': category_payload._partkey,
            'sortkey': category_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return category_payload


@pytest.fixture(scope='function')
def insert_some_product_categories(request):
    category_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    user_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    image_url = get_product_category_image_url(shop_uuid=shop_uuid, owner_uuid=owner_uuid, category_uuid=category_uuid)

    category_first = put_category_to_db(owner_uuid, shop_uuid, user_uuid, sort_index=0)
    category_second = put_category_to_db(owner_uuid, shop_uuid, user_uuid, sort_index=0)
    category_inactive = put_category_to_db(owner_uuid, shop_uuid, user_uuid, sort_index=0, inactive=True)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': category_first._partkey,
            'sortkey': category_first._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': category_second._partkey,
            'sortkey': category_second._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': category_inactive._partkey,
            'sortkey': category_inactive._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "category_first, category_second, category_inactive")(category_first, category_second, category_inactive)


def get_product_image_url(owner_uuid, shop_uuid, product_uuid):
    bucket_url = s3_key_structure.products_base_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        file_uuid=uuid.uuid4(),
        image_extention='svg'
    )
    return s3_key_structure.product_category_image_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
        file_name=bucket_url
    )


def get_product_base_info(owner_uuid, product_uuid, shop_uuid, user_uuid):
    image_url = get_product_image_url(owner_uuid=owner_uuid, shop_uuid=shop_uuid, product_uuid=product_uuid)
    product_payload = dto_products.ProductBaseInfo(
        uuid_=product_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        title="Test Product",
        description="Test Product Description",
        category_uuids=[
            uuid.uuid4(),
            uuid.uuid4(),
        ],
        inactive=False,
        date_create=datetime.datetime.now().isoformat(),
        image_url=image_url,
        record_type=db_keys_structure.product_base_record_type,
    )
    product_payload._partkey = db_keys_structure.product_base_partkey.format(shop_uuid=shop_uuid)
    product_payload._sortkey = db_keys_structure.product_base_sortkey.format(product_uuid=product_uuid)
    return product_payload


@pytest.fixture(scope='function')
def insert_product_base_info(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    product_uuid = uuid.uuid4()
    product_payload = get_product_base_info(owner_uuid, product_uuid, shop_uuid, user_uuid)
    db_utils.get_gen_table().put_item(Item=product_payload.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': product_payload._partkey,
            'sortkey': product_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return product_payload


def get_product_variant_image_urls(owner_uuid, shop_uuid, product_uuid, variant_uuid):
    image_urls = []
    for i in range(2):
        bucket_url = s3_key_structure.products_option_file_path.format(
            owner_uuid=owner_uuid,
            shop_uuid=shop_uuid,
            product_uuid=product_uuid,
            option_uuid=variant_uuid,
            file_uuid=uuid.uuid4(),
            image_extention='svg'
        )
        image_url = s3_key_structure.product_category_image_url.format(
            bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
            bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
            file_name=bucket_url
        )
        image_urls.append(image_url)
    return image_urls


def get_product_variant_options():
    options = []
    for i in range(2):
        options.append(
            dto_product_variants.ProductVariantOption(
                title=''.join(random.choice(string.ascii_lowercase) for i in range(10)),
                article=''.join(random.choice(string.ascii_lowercase) for i in range(10)),
                price=round(random.uniform(100, 2), 2),
                weight=random.randint(10, 100),
                quantity=random.randint(1, 10),
            )
        )
    return options

def get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid, inactive=None):
    inactive = False if inactive is None else inactive
    variant_uuid = uuid.uuid4()

    image_urls = get_product_variant_image_urls(
        owner_uuid=owner_uuid, shop_uuid=shop_uuid, product_uuid=product_uuid, variant_uuid=variant_uuid)
    options = get_product_variant_options()
    variant_payload = dto_product_variants.ProductVariant(
        uuid_=variant_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        title="Test Variant",
        options=options,
        image_urls=image_urls,
        inactive=inactive,
        date_create=datetime.datetime.now().isoformat(),
        record_type=db_keys_structure.product_variant_record_type,
    )
    variant_payload._partkey = db_keys_structure.product_variant_partkey.format(shop_uuid=shop_uuid)
    variant_payload._sortkey = db_keys_structure.product_variant_sortkey.format(
        product_uuid=product_uuid, variant_uuid=variant_uuid
    )
    return variant_payload


@pytest.fixture(scope='function')
def insert_product_variant(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    product_uuid = uuid.uuid4()
    variant_payload = get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid)
    db_utils.get_gen_table().put_item(Item=variant_payload.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': variant_payload._partkey,
            'sortkey': variant_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return variant_payload


@pytest.fixture(scope='function')
def insert_some_product_variants(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    product_uuid = uuid.uuid4()
    variant_payload_1  = get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid)
    variant_payload_2  = get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid)
    variant_payload_3  = get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid, inactive=True)
    db_utils.get_gen_table().put_item(Item=variant_payload_1.to_record())
    db_utils.get_gen_table().put_item(Item=variant_payload_2.to_record())
    db_utils.get_gen_table().put_item(Item=variant_payload_3.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': variant_payload_1._partkey,
            'sortkey': variant_payload_1._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': variant_payload_2._partkey,
            'sortkey': variant_payload_2._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': variant_payload_3._partkey,
            'sortkey': variant_payload_3._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "variant_active, variant_active_second, variant_inactive")(
        variant_payload_1, variant_payload_2, variant_payload_3
    )


def get_product_extra_kit(owner_uuid, product_uuid, shop_uuid, user_uuid, inactive=None):
    inactive = False if inactive is None else inactive
    extra_kit_uuid = uuid.uuid4()

    extra_kit_payload = dto_product_extra_kits.ProductExtraKit(
        uuid_=extra_kit_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        product_uuid=product_uuid,
        title="Test Extra Kit",
        price=100.10,
        addons=[
            "Test",
            "Testik"
        ],
        inactive=inactive,
        date_create=datetime.datetime.now().isoformat(),
        record_type=db_keys_structure.product_extra_kits_record_type,
    )
    extra_kit_payload._partkey = db_keys_structure.product_extra_kits_partkey.format(shop_uuid=shop_uuid)
    extra_kit_payload._sortkey = db_keys_structure.product_extra_kits_sortkey.format(
        product_uuid=product_uuid, extra_kit_uuid=extra_kit_uuid
    )
    return extra_kit_payload


@pytest.fixture(scope='function')
def insert_product_extra_kit(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    product_uuid = uuid.uuid4()
    extra_kit_payload = get_product_extra_kit(owner_uuid, product_uuid, shop_uuid, user_uuid)
    db_utils.get_gen_table().put_item(Item=extra_kit_payload.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': extra_kit_payload._partkey,
            'sortkey': extra_kit_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return extra_kit_payload


@pytest.fixture(scope='function')
def insert_some_product_extra_kits(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    product_uuid = uuid.uuid4()
    extra_kit_payload_firts = get_product_extra_kit(owner_uuid, product_uuid, shop_uuid, user_uuid)
    extra_kit_payload_second = get_product_extra_kit(owner_uuid, product_uuid, shop_uuid, user_uuid)
    extra_kit_payload_inactive = get_product_extra_kit(owner_uuid, product_uuid, shop_uuid, user_uuid, inactive=True)
    db_utils.get_gen_table().put_item(Item=extra_kit_payload_firts.to_record())
    db_utils.get_gen_table().put_item(Item=extra_kit_payload_second.to_record())
    db_utils.get_gen_table().put_item(Item=extra_kit_payload_inactive.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': extra_kit_payload_firts._partkey,
            'sortkey': extra_kit_payload_firts._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': extra_kit_payload_second._partkey,
            'sortkey': extra_kit_payload_second._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': extra_kit_payload_inactive._partkey,
            'sortkey': extra_kit_payload_inactive._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "extra_kit_firts, extra_kit_second, extra_kit_inactive")(
        extra_kit_payload_firts, extra_kit_payload_second, extra_kit_payload_inactive
    )


@pytest.fixture(scope='function')
def insert_product(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    product_uuid = uuid.uuid4()
    product_payload = get_product_base_info(owner_uuid, product_uuid, shop_uuid, user_uuid)
    variant_payload_first  = get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid)
    variant_payload_second  = get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid)
    extra_kit_payload = get_product_extra_kit(owner_uuid, product_uuid, shop_uuid, user_uuid)
    product_payload.price = min(
        min(option.price for option in variant_payload_first.options),
        min(option.price for option in variant_payload_second.options)
    )

    db_utils.get_gen_table().put_item(Item=product_payload.to_record())
    db_utils.get_gen_table().put_item(Item=variant_payload_first.to_record())
    db_utils.get_gen_table().put_item(Item=variant_payload_second.to_record())
    db_utils.get_gen_table().put_item(Item=extra_kit_payload.to_record())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': product_payload._partkey,
            'sortkey': product_payload._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': variant_payload_first._partkey,
            'sortkey': variant_payload_first._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': variant_payload_second._partkey,
            'sortkey': variant_payload_second._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': extra_kit_payload._partkey,
            'sortkey': extra_kit_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "product, product_variant_first, product_variant_second, product_extra_kit")(
        product_payload, variant_payload_first, variant_payload_second, extra_kit_payload
    )


def put_to_db_product(owner_uuid, shop_uuid, user_uuid):
    product_uuid = uuid.uuid4()

    class Items(pydantic.BaseModel):
        product: dto_products.ProductBaseInfo = get_product_base_info(owner_uuid, product_uuid, shop_uuid, user_uuid)
        variant_firts: dto_product_variants.ProductVariant = get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid)
        variant_second: dto_product_variants.ProductVariant = get_product_variant(owner_uuid, product_uuid, shop_uuid, user_uuid)
        extra_kit: dto_product_extra_kits.ProductExtraKit = get_product_extra_kit(owner_uuid, product_uuid, shop_uuid, user_uuid)

    items = Items()
    items.product.price = min(
        min(option.price for option in items.variant_firts.options),
        min(option.price for option in items.variant_second.options)
    )
    db_utils.get_gen_table().put_item(Item=items.product.to_record())
    db_utils.get_gen_table().put_item(Item=items.variant_firts.to_record())
    db_utils.get_gen_table().put_item(Item=items.variant_second.to_record())
    db_utils.get_gen_table().put_item(Item=items.extra_kit.to_record())
    return items


@pytest.fixture(scope='function')
def insert_some_products(request):

    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()

    product_firts = put_to_db_product(owner_uuid, shop_uuid, user_uuid)
    product_second = put_to_db_product(owner_uuid, shop_uuid, user_uuid)

    def resource_teardown():
        for _, val in iter(product_firts):
            db_utils.get_gen_table().delete_item(Key={
                'partkey': val._partkey,
                'sortkey': val._sortkey
            })
        for _, val in iter(product_second):
            db_utils.get_gen_table().delete_item(Key={
                'partkey': val._partkey,
                'sortkey': val._sortkey
            })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "product_firts, product_second")(product_firts, product_second)


def generate_test_schedule():
    weeks = dto_delivery_self_pickup.DeliverySelfPickupWeekDays(
        monday=dto_delivery_self_pickup.DeliverySelfPickupTimes(
            time_start="09:00",
            time_stop="20:00"
        ),
        tuesday=dto_delivery_self_pickup.DeliverySelfPickupTimes(
            time_start="09:00",
            time_stop="20:00"
        ),
        wednesday=dto_delivery_self_pickup.DeliverySelfPickupTimes(
            time_start="09:00",
            time_stop="20:00"
        ),
        thursday=dto_delivery_self_pickup.DeliverySelfPickupTimes(
            time_start="09:00",
            time_stop="20:00"
        ),
        friday=dto_delivery_self_pickup.DeliverySelfPickupTimes(
            time_start="10:00",
            time_stop="17:00"
        ),
        saturday=None,
        sunday=None,
    )
    return weeks


def put_to_db_delivery_self_pickup(owner_uuid, shop_uuid, user_uuid, inactive=False):
    self_pickup_uuid = uuid.uuid4()
    self_pickup_payload = dto_delivery_self_pickup.DeliverySelfPickup(
        uuid_=self_pickup_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        title="Test Delivery Self Pickup",
        description="Test Delivery Self Pickup Description",
        contact_phone=TEST_PHONE,
        contact_tg_username=TEST_USER.tg_username,
        schedule=generate_test_schedule(),
        inactive=inactive,
        date_create=datetime.datetime.now().isoformat(),
        record_type=db_keys_structure.delivery_self_pickup_record_type,
    )
    self_pickup_payload._partkey = db_keys_structure.delivery_self_pickup_partkey.format(shop_uuid=shop_uuid)
    self_pickup_payload._sortkey = db_keys_structure.delivery_self_pickup_sortkey.format(
        self_pickup_uuid=self_pickup_uuid)
    db_utils.get_gen_table().put_item(Item=self_pickup_payload.to_record())
    return self_pickup_payload


@pytest.fixture(scope='function')
def insert_delivery_self_pickup(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    delivery_self_pickup = put_to_db_delivery_self_pickup(owner_uuid, shop_uuid, user_uuid)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': delivery_self_pickup._partkey,
            'sortkey': delivery_self_pickup._sortkey
        })

    request.addfinalizer(resource_teardown)

    return delivery_self_pickup


@pytest.fixture(scope='function')
def insert_some_delivery_self_pickup(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    self_pickup_first = put_to_db_delivery_self_pickup(owner_uuid, shop_uuid, user_uuid)
    self_pickup_second = put_to_db_delivery_self_pickup(owner_uuid, shop_uuid, user_uuid)
    self_pickup_inactive = put_to_db_delivery_self_pickup(owner_uuid, shop_uuid, user_uuid, inactive=True)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': self_pickup_first._partkey,
            'sortkey': self_pickup_first._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': self_pickup_second._partkey,
            'sortkey': self_pickup_second._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': self_pickup_inactive._partkey,
            'sortkey': self_pickup_inactive._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "self_pickup_first, self_pickup_second, self_pickup_inactive")(self_pickup_first, self_pickup_second, self_pickup_inactive)


def put_to_db_delivery_manual(owner_uuid, shop_uuid, user_uuid, inactive=False):
    delivery_manual_uuid = uuid.uuid4()
    delivery_manual_payload = dto_delivery_manual.DeliveryManual(
        uuid_=delivery_manual_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        title="Test Delivery Manual",
        description="Test Delivery Manual Description",
        contact_phone=TEST_PHONE,
        contact_tg_username=TEST_USER.tg_username,
        price=100.1,
        inactive=inactive,
        date_create=datetime.datetime.now().isoformat(),
        record_type=db_keys_structure.delivery_manual_record_type,
    )
    delivery_manual_payload._partkey = db_keys_structure.delivery_manual_partkey.format(shop_uuid=shop_uuid)
    delivery_manual_payload._sortkey = db_keys_structure.delivery_manual_sortkey.format(
        delivery_manual_uuid=delivery_manual_uuid)
    db_utils.get_gen_table().put_item(Item=delivery_manual_payload.to_record())
    return delivery_manual_payload


@pytest.fixture(scope='function')
def insert_delivery_manual(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    delivery_manual = put_to_db_delivery_manual(owner_uuid, shop_uuid, user_uuid)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': delivery_manual._partkey,
            'sortkey': delivery_manual._sortkey
        })

    request.addfinalizer(resource_teardown)

    return delivery_manual


@pytest.fixture(scope='function')
def insert_some_delivery_manual(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    delivery_manual_first = put_to_db_delivery_manual(owner_uuid, shop_uuid, user_uuid)
    delivery_manual_second = put_to_db_delivery_manual(owner_uuid, shop_uuid, user_uuid)
    delivery_manual_inactive = put_to_db_delivery_manual(owner_uuid, shop_uuid, user_uuid, inactive=True)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': delivery_manual_first._partkey,
            'sortkey': delivery_manual_first._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': delivery_manual_second._partkey,
            'sortkey': delivery_manual_second._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': delivery_manual_inactive._partkey,
            'sortkey': delivery_manual_inactive._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "delivery_manual_first, delivery_manual_second, delivery_manual_inactive")(delivery_manual_first, delivery_manual_second, delivery_manual_inactive)


def put_to_db_template(inactive: bool = False):
    template_uuid = uuid.uuid4()

    template_payload = dto_template.Template(
        uuid_=template_uuid,
        title="test template",
        description="test template description",
        photo_url=get_template_photo_url(template_uuid),
        template_url="https://fake.com/",
        exclusive_owner_uuid=None,
        date_create=datetime.datetime.now().isoformat(),
        inactive=inactive,
        record_type=db_keys_structure.template_record_type,
    )
    template_payload._partkey = template_payload._partkey
    template_payload._sortkey = template_payload._sortkey.format(uuid=template_uuid)
    db_utils.get_gen_table().put_item(Item=template_payload.to_record())

    return template_payload


@pytest.fixture(scope='function')
def insert_shop_with_active_template(request):
    owner_uuid = uuid.uuid4()

    template_payload = put_to_db_template()
    shop_payload = put_shop_to_db(owner_uuid=owner_uuid, inactive=False, template_uuid=template_payload.uuid_)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
          'partkey': template_payload._partkey,
          'sortkey': template_payload._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
          'partkey': shop_payload._partkey,
          'sortkey': shop_payload._sortkey
        })

    request.addfinalizer(resource_teardown)
    return shop_payload, template_payload


@pytest.fixture(scope='function')
def insert_shop_with_inactive_template(request):
    owner_uuid = uuid.uuid4()

    template_payload = put_to_db_template(inactive=True)
    shop_payload = put_shop_to_db(owner_uuid=owner_uuid, inactive=False, template_uuid=template_payload.uuid_)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': template_payload._partkey,
            'sortkey': template_payload._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': shop_payload._partkey,
            'sortkey': shop_payload._sortkey
        })
    request.addfinalizer(resource_teardown)

    return shop_payload, template_payload


def get_rubric_image_url(owner_uuid, shop_uuid):
    bucket_url = s3_key_structure.infopages_rubric_file_path.format(
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        file_uuid=uuid.uuid4(),
        image_extention="svg"
    )
    image_url = s3_key_structure.infopages_rubric_image_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
        file_name=bucket_url
    )
    return image_url


def put_to_db_infopages_rubric(owner_uuid, shop_uuid, user_uuid, inactive=False):
    rubric_uuid = uuid.uuid4()
    image_url = get_rubric_image_url(owner_uuid, shop_uuid)
    rubric_payload = dto_infopages_rubrics.Rubric(
        uuid_=rubric_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        title="Test InfoPages Rubric",
        description="Test InfoPages Rubric Description",
        inactive=inactive,
        date_create=datetime.datetime.now().isoformat(),
        hex_color="FFFFFF",
        sort_index=1,
        image_url=image_url,
        record_type=db_keys_structure.infopages_rubrics_record_type,
    )
    rubric_payload._partkey = db_keys_structure.infopages_rubrics_partkey.format(shop_uuid=shop_uuid)
    rubric_payload._sortkey = db_keys_structure.infopages_rubrics_sortkey.format(rubric_uuid=rubric_uuid)
    db_utils.get_gen_table().put_item(Item=rubric_payload.to_record())
    return rubric_payload


@pytest.fixture(scope='function')
def insert_infopages_rubric(request):
    owner_uuid = uuid.uuid4()
    user_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    rubric_payload = put_to_db_infopages_rubric(owner_uuid, shop_uuid, user_uuid)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': rubric_payload._partkey,
            'sortkey': rubric_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return rubric_payload


@pytest.fixture(scope='function')
def insert_some_infopages_rubrics(request):
    owner_uuid = uuid.uuid4()
    user_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    rubric_payload_first = put_to_db_infopages_rubric(owner_uuid, shop_uuid, user_uuid)
    rubric_payload_second = put_to_db_infopages_rubric(owner_uuid, shop_uuid, user_uuid)
    rubric_payload_inactive = put_to_db_infopages_rubric(owner_uuid, shop_uuid, user_uuid, inactive=True)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': rubric_payload_first._partkey,
            'sortkey': rubric_payload_first._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': rubric_payload_second._partkey,
            'sortkey': rubric_payload_second._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': rubric_payload_inactive._partkey,
            'sortkey': rubric_payload_inactive._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple("Setup", "rubric_first, rubric_second, rubric_inactive")(rubric_payload_first, rubric_payload_second, rubric_payload_inactive)


def get_post_image_urls(owner_uuid, shop_uuid, post_uuid, count=2):
    image_urls = []
    for i in range(count):
        image_extension = "svg"
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
        image_urls.append(image_url)
    return image_urls


def put_to_db_infopages_post(user_uuid, owner_uuid, shop_uuid, rubric_uuid, inactive=False):
    post_uuid = uuid.uuid4()
    image_urls = get_post_image_urls(owner_uuid, shop_uuid, post_uuid)
    post_payload = dto_infopages_posts.Post(
        uuid_=post_uuid,
        owner_uuid=owner_uuid,
        user_uuid=user_uuid,
        shop_uuid=shop_uuid,
        rubric_uuid=rubric_uuid,
        title="Test Post",
        description="Test Post Description",
        inactive=inactive,
        date_create=datetime.datetime.now().isoformat(),
        image_urls=image_urls,
        record_type=db_keys_structure.infopages_posts_record_type,
    )
    post_payload._partkey = db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid)
    post_payload._sortkey = db_keys_structure.infopages_posts_sortkey.format(post_uuid=post_uuid)
    db_utils.get_gen_table().put_item(Item=post_payload.to_record())

    return post_payload


@pytest.fixture(scope='function')
def insert_infopages_post(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    rubric_uuid = uuid.uuid4()
    post_payload = put_to_db_infopages_post(user_uuid, owner_uuid, shop_uuid, rubric_uuid)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': post_payload._partkey,
            'sortkey': post_payload._sortkey
        })

    request.addfinalizer(resource_teardown)

    return post_payload


@pytest.fixture(scope='function')
def insert_some_infopages_posts(request):
    user_uuid = uuid.uuid4()
    owner_uuid = uuid.uuid4()
    shop_uuid = uuid.uuid4()
    rubric_first_uuid = uuid.uuid4()
    rubric_second_uuid = uuid.uuid4()

    post_rubric_first_one = put_to_db_infopages_post(user_uuid, owner_uuid, shop_uuid, rubric_first_uuid)
    post_rubric_first_two = put_to_db_infopages_post(user_uuid, owner_uuid, shop_uuid, rubric_first_uuid)
    post_rubric_first_inactive = put_to_db_infopages_post(user_uuid, owner_uuid, shop_uuid, rubric_first_uuid, inactive=True)
    post_rubric_second = put_to_db_infopages_post(user_uuid, owner_uuid, shop_uuid, rubric_second_uuid)

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': post_rubric_first_one._partkey,
            'sortkey': post_rubric_first_one._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': post_rubric_first_two._partkey,
            'sortkey': post_rubric_first_two._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': post_rubric_first_inactive._partkey,
            'sortkey': post_rubric_first_inactive._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': post_rubric_second._partkey,
            'sortkey': post_rubric_second._sortkey
        })

    request.addfinalizer(resource_teardown)

    return namedtuple(
        "Setup", "post_rubric_first_one, post_rubric_first_two, post_rubric_first_inactive, post_rubric_second"
    )(
        post_rubric_first_one, post_rubric_first_two, post_rubric_first_inactive, post_rubric_second
    )


@pytest.fixture(scope='function')
def insert_shop_with_expired_subscription(request):
    owner_uuid = uuid.uuid4()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

    shop_payload1 = put_shop_to_db(owner_uuid=owner_uuid, inactive=False, template_uuid=uuid.uuid4(),
                                   subscription_active=False, subscription_expire_at=yesterday.isoformat())

    shop_payload2 = put_shop_to_db(owner_uuid=owner_uuid, inactive=False, template_uuid=uuid.uuid4(),
                                   subscription_active=True, subscription_expire_at=yesterday.isoformat())

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
          'partkey': shop_payload1._partkey,
          'sortkey': shop_payload1._sortkey
        })
        db_utils.get_gen_table().delete_item(Key={
            'partkey': shop_payload2._partkey,
            'sortkey': shop_payload2._sortkey
        })

    request.addfinalizer(resource_teardown)

    return shop_payload1, shop_payload2
