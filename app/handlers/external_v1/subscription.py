import datetime
import logging

from app.dto.shop import Shop, ShopUpdateSubscription
from app.dto.common import UUIDasStr
from app.db import keys_structure as db_keys_structure, common as db_common

logger = logging.getLogger(__name__)


def check_subscription(shop_item: dict) -> bool:
    """Функция получаем объект магазина и проверяет его подписку"""
    date = datetime.datetime.now().isoformat()
    subscription_status = True

    if not shop_item['subscription_active']:
        logger.error(f"Subscription ended", extra={'user': 'check_subscription_func'})
        subscription_status = False
    if shop_item['subscription_expire_at'] < date and shop_item['subscription_active']:
        logger.error(f"Subscription ended but sub flag=true", extra={'user': 'check_subscription_func'})
        update_subscription_status(shop_uuid=shop_item['uuid_'], new_subscription_status=False)
        subscription_status = False

    return subscription_status


def update_subscription_status(shop_uuid: UUIDasStr, new_subscription_status: bool) -> Shop:
    """Функция получаем uuid магазина и изменяет ему поля подписки"""

    shop_payload = ShopUpdateSubscription(
        subscription_active=new_subscription_status
    )

    shop_payload._partkey = db_keys_structure.shop_partkey
    shop_payload._sortkey = db_keys_structure.shop_sortkey.format(shop_uuid=shop_uuid)

    shop_updated = db_common.update_db_record(db_common.pydantic_db_update_helper(shop_payload))

    return Shop(**shop_updated)
