import fastapi
from fastapi import status as http_status


FileRequired = fastapi.HTTPException(
    status_code=http_status.HTTP_409_CONFLICT,
    detail='Фотография отсутствует!'
)

CategoryNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Запрашиваемой категории товаров не существует!'
)


VariantNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Такой вариант товара отсутствует!'
)


ExtraKitNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Дополнительный набор для товара отсутствует!'
)


ProductNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Такой товар отсутствует!'
)
