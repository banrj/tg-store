import fastapi

from app.dto import (
    common as common_dto,
    product_categories as dto_product_categories,
)
from app.handlers import (
    product_categories as handlers_product_categories
)

router = fastapi.APIRouter(prefix="/product_categories")


# TODO добавить проверку API KEY
@router.get(
    path='/{shop_uuid}',
    response_model=list[dto_product_categories.Category],
    tags=['Product Categories']
)
def get_product_categories_list(
        shop_uuid: common_dto.UUIDasStr,
):
    """
    Получить список категорий товаров.
    """
    return handlers_product_categories.handle_get_categories_list(shop_uuid=shop_uuid)


# TODO добавить проверку API KEY
@router.get(
    path='/{shop_uuid}/{category_uuid}',
    response_model=dto_product_categories.Category,
    tags=['Product Categories']
)
def get_product_category(
        shop_uuid: common_dto.UUIDasStr,
        category_uuid: common_dto.UUIDasStr,
):
    """
    Получить информацию о категории товаров.
    """
    return handlers_product_categories.handle_get_category(shop_uuid=shop_uuid, category_uuid=category_uuid,)

