import fastapi
from fastapi import status as http_status


WrongRubric = fastapi.HTTPException(
    status_code=http_status.HTTP_409_CONFLICT,
    detail='Указана неверная рубрика информационной страницы.'
)

RubricNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Запрашиваемой рубрики информационных страниц не существует!'
)
