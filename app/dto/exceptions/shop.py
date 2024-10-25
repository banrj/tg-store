import fastapi
from fastapi import status as http_status

ShopNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Магазин не найден'
)

CategoriesConflict = fastapi.HTTPException(
    status_code=http_status.HTTP_409_CONFLICT,
    detail='ID категорий должны быть уникальными'
)

ShopInactive = fastapi.HTTPException(
    status_code=http_status.HTTP_400_BAD_REQUEST,
    detail='Магазин неактивен'
)

IncorrectShopOwner = fastapi.HTTPException(
    status_code=http_status.HTTP_403_FORBIDDEN,
    detail='Удалить магазин может только его владелец!'
)

ShopWithoutTemplate = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='У магазина нет шаблона'
)