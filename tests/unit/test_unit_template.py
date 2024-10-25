from unittest import mock

from app.dto import template as dto_template
from app.handlers import template as template_handlers
from app.db import common as db_common, keys_structure as db_keys_structure, utils as db_utils, s3_key_structure
from app import settings

from tests import utils as test_utils


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_add_template(_mock_upload_file_to_s3, request):
    data = dto_template.TemplateRequestBody(
        title="test template",
        description="test description",
        template_url="https://fake.com/",
    )

    template = template_handlers.handle_add_template(data=data, photo=test_utils.get_image_file())

    template_db = db_common.get_db_item(
        partkey=db_keys_structure.template_partkey,
        sortkey=db_keys_structure.template_sortkey.format(uuid=template.uuid_)
    )

    bucket_url = s3_key_structure.template_file_path.format(template_uuid=template.uuid_, photo_extention="svg")
    photo_url = s3_key_structure.template_photo_url.format(
        bucket_url_prefix=settings.YC_PRODUCTS_BUCKET_URL_PREFIX,
        bucket_name=settings.YC_SERVICE_BUCKET_NAME,
        file_name=bucket_url
    )

    def resource_teardown():
        db_utils.get_gen_table().delete_item(Key={
            'partkey': template_db["partkey"],
            'sortkey': template_db["sortkey"]
        })

    request.addfinalizer(resource_teardown)

    assert str(template.uuid_) == template_db["uuid_"]
    assert template.title == template_db["title"] and template_db["title"] == data.title
    assert template.description == template_db["description"] and template_db["description"] == data.description
    assert str(template.template_url) == template_db["template_url"] and template_db["template_url"] == str(data.template_url)
    assert str(template.photo_url) == photo_url
    assert template_db["photo_url"] == photo_url
    assert template.date_create == template_db["date_create"]
    assert template.date_update == template_db["date_update"]
    assert template_db["record_type"] == db_keys_structure.template_record_type


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_template(_mock_upload_file_to_s3, insert_active_template, request):
    data = dto_template.TemplateUpdateBody(
        title="test shop update",
        template_url="https://fakes.com/",
    )

    template = template_handlers.handle_update_template(
        template_uuid=insert_active_template.uuid_, data=data, photo=test_utils.get_image_file()
    )

    assert template.uuid_ == insert_active_template.uuid_
    assert template.title != insert_active_template.title and template.title == data.title
    assert template.description == insert_active_template.description
    assert template.template_url != insert_active_template.template_url and template.template_url == data.template_url
    assert template.photo_url == insert_active_template.photo_url
    assert template.date_create == insert_active_template.date_create
    assert template.date_update != insert_active_template.date_update
    assert template.record_type == db_keys_structure.template_record_type


def test_update_template_without_file(insert_active_template, request):
    data = dto_template.TemplateUpdateBody(
        title="test shop update",
        template_url="https://fakes.com/",
    )

    template = template_handlers.handle_update_template(template_uuid=insert_active_template.uuid_, data=data, photo='')

    assert template.uuid_ == insert_active_template.uuid_
    assert template.title != insert_active_template.title and template.title == data.title
    assert template.description == insert_active_template.description
    assert template.template_url != insert_active_template.template_url and template.template_url == data.template_url
    assert template.photo_url == insert_active_template.photo_url
    assert template.date_create == insert_active_template.date_create
    assert template.date_update != insert_active_template.date_update
    assert template.record_type == db_keys_structure.template_record_type


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_template_without_data(_mock_upload_file_to_s3, insert_active_template, request):
    data = dto_template.TemplateUpdateBody()

    template = template_handlers.handle_update_template(
        template_uuid=insert_active_template.uuid_, data=data, photo=test_utils.get_image_file()
    )

    assert template.uuid_ == insert_active_template.uuid_
    assert template.title == insert_active_template.title
    assert template.description == insert_active_template.description
    assert template.template_url == insert_active_template.template_url
    assert template.photo_url == insert_active_template.photo_url
    assert template.date_create == insert_active_template.date_create
    assert template.date_update != insert_active_template.date_update
    assert template.record_type == db_keys_structure.template_record_type


def test_get_templates_list(insert_active_template, insert_inactive_template, request):
    templates = template_handlers.handle_get_list_templates()

    assert len(templates) == 2
    for t in templates:
        if t.uuid_ == insert_active_template.uuid_:
            assert t.uuid_ == insert_active_template.uuid_
            assert t.title == insert_active_template.title
            assert t.description == insert_active_template.description
            assert t.template_url == insert_active_template.template_url
            assert t.photo_url == insert_active_template.photo_url
            assert t.date_create == insert_active_template.date_create
            assert t.date_update != insert_active_template.date_update
            assert t.inactive is False
            assert t.record_type == db_keys_structure.template_record_type
        else:
            assert t.uuid_ == insert_inactive_template.uuid_
            assert t.title == insert_inactive_template.title
            assert t.description == insert_inactive_template.description
            assert t.template_url == insert_inactive_template.template_url
            assert t.photo_url == insert_inactive_template.photo_url
            assert t.date_create == insert_inactive_template.date_create
            assert t.date_update != insert_inactive_template.date_update
            assert t.inactive is True
            assert t.record_type == db_keys_structure.template_record_type


def test_get_template(insert_active_template, request):
    template = template_handlers.handle_get_template(template_uuid=insert_active_template.uuid_)

    assert template.uuid_ == insert_active_template.uuid_
    assert template.title == insert_active_template.title
    assert template.description == insert_active_template.description
    assert template.template_url == insert_active_template.template_url
    assert template.photo_url == insert_active_template.photo_url
    assert template.date_create == insert_active_template.date_create
    assert template.date_update != insert_active_template.date_update
    assert template.inactive is False
    assert template.record_type == db_keys_structure.template_record_type


def test_delete_template(insert_active_template, request):
    template = template_handlers.handle_delete_template(template_uuid=insert_active_template.uuid_)

    assert template.uuid_ == insert_active_template.uuid_
    assert template.title == insert_active_template.title
    assert template.description == insert_active_template.description
    assert template.template_url == insert_active_template.template_url
    assert template.photo_url == insert_active_template.photo_url
    assert template.date_create == insert_active_template.date_create
    assert template.date_update != insert_active_template.date_update
    assert insert_active_template.inactive is False and template.inactive is True
    assert template.record_type == db_keys_structure.template_record_type
