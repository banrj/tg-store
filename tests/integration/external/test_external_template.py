from app.settings import settings
from app.db import common as db_common, keys_structure as db_keys_structure


def test_redirect_template(insert_shop_with_active_template, test_client, request):
    shop_uuid = insert_shop_with_active_template[0].uuid_
    owner_uuid = insert_shop_with_active_template[0].owner_uuid
    template_uuid = insert_shop_with_active_template[1].uuid_
    template_url = insert_shop_with_active_template[1].template_url

    url = f'/template/templates/redirect/{shop_uuid}'
    response = test_client.get(url=url, allow_redirects=False)

    assert response.status_code == 302

    assert response.headers["location"] == (f"{template_url}?"
                                            f"shop_uuid={shop_uuid}&owner_uuid={owner_uuid}" 
                                            f"&template_uuid={template_uuid}&access_key=key")


def test_redirect_without_template(insert_active_shop, test_client, request):
    shop_uuid = insert_active_shop.uuid_

    url = f'/template/templates/redirect/{shop_uuid}'
    response = test_client.get(url=url, allow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == settings.DEFAULT_REDIRECT_URL


def test_redirect_with_inactive_shop(insert_inactive_shop, test_client, request):
    shop_uuid = insert_inactive_shop.uuid_

    url = f'/template/templates/redirect/{shop_uuid}'
    response = test_client.get(url=url, allow_redirects=False)

    assert response.status_code == 307

    assert response.headers["location"] == settings.DEFAULT_REDIRECT_URL


def test_redirect_with_inactive_template(insert_shop_with_inactive_template, test_client, request):
    shop_uuid = insert_shop_with_inactive_template[0].uuid_
    owner_uuid = insert_shop_with_inactive_template[0].owner_uuid
    template_uuid = insert_shop_with_inactive_template[1].uuid_
    template_url = insert_shop_with_inactive_template[1].template_url
    url = f'template/templates/redirect/{shop_uuid}'
    response = test_client.get(url=url, allow_redirects=False)

    assert response.status_code == 302

    assert response.headers["location"] == (f"{template_url}?"
                                            f"shop_uuid={shop_uuid}&owner_uuid={owner_uuid}" 
                                            f"&template_uuid={template_uuid}&access_key=key")


def test_redirect_with_shop_without_subscription(insert_shop_with_expired_subscription, test_client, request):
    shop_uuid1 = insert_shop_with_expired_subscription[0].uuid_
    shop_uuid2 = insert_shop_with_expired_subscription[1].uuid_

    url = f'template/templates/redirect/{shop_uuid1}'
    response1 = test_client.get(url=url, allow_redirects=False)
    assert response1.status_code == 307

    assert response1.headers["location"] == settings.DEFAULT_REDIRECT_URL

    url = f'template/templates/redirect/{shop_uuid2}'
    response2 = test_client.get(url=url, allow_redirects=False)
    assert response2.status_code == 307

    assert response2.headers["location"] == settings.DEFAULT_REDIRECT_URL

    shop_db = db_common.get_db_item(
        partkey=db_keys_structure.shop_partkey,
        sortkey=db_keys_structure.shop_sortkey.format(shop_uuid=shop_uuid2)
    )

    assert shop_db['subscription_active'] != insert_shop_with_expired_subscription[1].subscription_active
