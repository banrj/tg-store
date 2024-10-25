import logging

from fastapi.responses import RedirectResponse
from app.dto import common as dto_common
from app.db import keys_structure as db_keys_structure, common as db_common
from app.settings import settings
from app.handlers.external_v1.subscription import check_subscription

logger = logging.getLogger(__name__)


def handle_get_template_redirect(shop_uuid: dto_common.UUIDasStr) -> RedirectResponse:
    shop_item = db_common.get_db_item(
        partkey=db_keys_structure.shop_partkey,
        sortkey=db_keys_structure.shop_sortkey.format(shop_uuid=shop_uuid)
    )
    default_url = f"{settings.DEFAULT_REDIRECT_URL}"
    if not shop_item or not shop_item['inactive']:
        logger.error(f"Shop not found", extra={'user': 'redirect_request'})
        return RedirectResponse(default_url, status_code=307)
    if not check_subscription(shop_item=shop_item):
        logger.error(f"Subscription has expired at shop № {shop_item['uuid_']}", extra={'user': 'redirect_request'})
        return RedirectResponse(default_url, status_code=307)
    template_item = db_common.get_db_item(
        partkey=db_keys_structure.template_partkey,
        sortkey=db_keys_structure.template_sortkey.format(uuid=shop_item['template_uuid'])
    )
    if not template_item:
        logger.error(f"Template not found", extra={'user': 'redirect_request'})
        return RedirectResponse(default_url, status_code=307)
    elif not template_item.get('template_url', None):
        logger.error(f"Template has no link", extra={'user': 'redirect_request'})
        return RedirectResponse(default_url, status_code=307)
    elif template_item['inactive']:
        logger.error(f"Template {template_item['uuid_']} inactive", extra={'user': 'redirect_request'})

    url = (f"{template_item['template_url']}?shop_uuid={shop_item['uuid_']}&"
           f"owner_uuid={shop_item['owner_uuid']}&template_uuid={shop_item['template_uuid']}&"
           f"access_key=key")
    return RedirectResponse(url, status_code=302)
