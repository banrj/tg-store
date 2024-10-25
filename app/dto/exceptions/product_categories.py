import fastapi
from fastapi import status as http_status


WrongCategory = fastapi.HTTPException(
    status_code=http_status.HTTP_409_CONFLICT,
    detail='Указана неверная категория товара. Такой нет в магазине'
)

CategoryNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Запрашиваемой категории товаров не существует!'
)
