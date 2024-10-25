import uuid
from unittest import mock

from app.db import keys_structure as db_keys_structure, common as db_common, utils as db_utils
from app.dto import infopages_posts as dto_infopages_posts
from conftest import TEST_USER_UUID


@mock.patch('app.utils.s3.upload_file_to_s3')
def test_add_infopages_post(_mock_upload_file_to_s3, test_client, request):
    owner_uuid = str(uuid.uuid4())
    shop_uuid = str(uuid.uuid4())
    rubric_uuid = str(uuid.uuid4())

    url = f'/infopages/posts/{owner_uuid}/{shop_uuid}'
    files = [('images', open("tests/utils/test.svg", "rb")), ('images', open("tests/utils/test.svg", "rb"))]
    request_body = dto_infopages_posts.PostCreateRequest(
        title="Test Post",
        description="Test Post Description",
        rubric_uuid=rubric_uuid,
    )

    response = test_client.post(url=url, data={'data': request_body.model_dump_json()}, files=files)
    response_body = response.json()

    pk = db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.infopages_posts_sortkey.format(post_uuid=response_body['uuid'])
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
    assert response_body['title'] == db_item['title'] == request_body.title
    assert response_body['description'] == db_item['description'] == request_body.description
    assert response_body['rubric_uuid'] == db_item['rubric_uuid'] == rubric_uuid
    assert len(response_body['image_urls']) == 2
    assert len(db_item['image_urls']) == 2
    assert db_item['partkey'] == pk
    assert db_item['sortkey'] == sk
    assert db_item['record_type'] == db_keys_structure.infopages_posts_record_type
    assert "infopages_posts" in response_body['image_urls'][0]
    assert db_item['inactive'] is False
    assert _mock_upload_file_to_s3.call_count == 2


@mock.patch('app.utils.s3.delete_files_from_s3')
@mock.patch('app.utils.s3.upload_file_to_s3')
def test_update_infopages_post(
        _mock_upload_file_to_s3, _mock_delete_files_from_s3, insert_infopages_post, test_client, request):

    owner_uuid = str(insert_infopages_post.owner_uuid)
    shop_uuid = str(insert_infopages_post.shop_uuid)
    post_uuid = str(insert_infopages_post.uuid_)

    request_body = dto_infopages_posts.PostUpdateRequest(
        title="Test Post",
        description="Test Post Description",
        rubric_uuid=uuid.uuid4(),
        image_urls=[insert_infopages_post.image_urls[0]],
        inactive=True,
    )

    url = f'/infopages/posts/{owner_uuid}/{shop_uuid}/{post_uuid}'
    files = [('images', open("tests/utils/test.svg", "rb")), ('images', open("tests/utils/test.svg", "rb"))]

    response = test_client.patch(url=url, data={'data': request_body.model_dump_json()}, files=files)
    response_body = response.json()

    assert response_body['uuid'] == post_uuid
    assert response_body['user_uuid'] == TEST_USER_UUID
    assert response_body['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == shop_uuid
    assert response_body['rubric_uuid'] == str(request_body.rubric_uuid)
    assert response_body['title'] == request_body.title
    assert response_body['description'] == request_body.description
    assert len(response_body['image_urls']) == 3
    assert str(insert_infopages_post.image_urls[0]) in response_body['image_urls']
    assert str(insert_infopages_post.image_urls[1]) not in response_body['image_urls']
    assert response_body['inactive'] is True
    assert _mock_upload_file_to_s3.call_count == 2
    assert _mock_delete_files_from_s3.call_count == 1


def test_get_infopages_post(test_client, insert_infopages_post, request):

    owner_uuid = str(insert_infopages_post.owner_uuid)
    shop_uuid = str(insert_infopages_post.shop_uuid)
    post_uuid = str(insert_infopages_post.uuid_)

    url = f'/infopages/posts/{shop_uuid}/{post_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    assert response_body['uuid'] == post_uuid
    assert response_body['user_uuid'] == str(insert_infopages_post.user_uuid)
    assert response_body['owner_uuid'] == owner_uuid
    assert response_body['shop_uuid'] == shop_uuid
    assert response_body['rubric_uuid'] == str(insert_infopages_post.rubric_uuid)
    assert response_body['title'] == insert_infopages_post.title
    assert response_body['description'] == insert_infopages_post.description
    assert response_body['image_urls'] == [str(i) for i in insert_infopages_post.image_urls]
    assert response_body['inactive'] is False


def test_get_list_of_shop_infopages_posts(test_client, insert_some_infopages_posts, request):

    shop_uuid = str(insert_some_infopages_posts.post_rubric_first_one.shop_uuid)

    url = f'/infopages/posts/list/by/{shop_uuid}/'
    response = test_client.get(url=url)
    response_body = response.json()

    uuids = [i['uuid'] for i in response_body]

    assert len(response_body) == 3
    assert str(insert_some_infopages_posts.post_rubric_first_one.uuid_) in uuids
    assert str(insert_some_infopages_posts.post_rubric_first_two.uuid_) in uuids
    assert str(insert_some_infopages_posts.post_rubric_second.uuid_) in uuids


def test_get_list_of_rubric_infopages_posts(test_client, insert_some_infopages_posts, request):

    shop_uuid = str(insert_some_infopages_posts.post_rubric_first_one.shop_uuid)
    rubric_uuid = str(insert_some_infopages_posts.post_rubric_first_one.rubric_uuid)

    url = f'/infopages/posts/list/by/{shop_uuid}/{rubric_uuid}'
    response = test_client.get(url=url)
    response_body = response.json()

    uuids = [i['uuid'] for i in response_body]

    assert len(response_body) == 2
    assert str(insert_some_infopages_posts.post_rubric_first_one.uuid_) in uuids
    assert str(insert_some_infopages_posts.post_rubric_first_two.uuid_) in uuids
    assert str(insert_some_infopages_posts.post_rubric_second.uuid_) not in uuids


def test_delete_infopages_post(test_client, insert_infopages_post, request):

    owner_uuid = str(insert_infopages_post.owner_uuid)
    shop_uuid = str(insert_infopages_post.shop_uuid)
    post_uuid = str(insert_infopages_post.uuid_)

    url = f'/infopages/posts/{owner_uuid}/{shop_uuid}/{post_uuid}'
    response = test_client.delete(url=url)
    response_body = response.json()

    pk = db_keys_structure.infopages_posts_partkey.format(shop_uuid=shop_uuid)
    sk = db_keys_structure.infopages_posts_sortkey.format(post_uuid=post_uuid)
    db_item = db_common.get_db_item(partkey=pk, sortkey=sk)

    assert response.status_code == 200
    assert db_item['uuid_'] == post_uuid
    assert db_item['user_uuid'] == TEST_USER_UUID
    assert db_item['owner_uuid'] == owner_uuid
    assert db_item['shop_uuid'] == shop_uuid
    assert db_item['rubric_uuid'] == str(insert_infopages_post.rubric_uuid)
    assert db_item['title'] == insert_infopages_post.title
    assert db_item['description'] == insert_infopages_post.description
    assert db_item['image_urls'] == [str(i) for i in insert_infopages_post.image_urls]
    assert db_item['inactive'] is True
