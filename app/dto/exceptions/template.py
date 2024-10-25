import fastapi
from fastapi import status as http_status


TemplateNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Шаблон не найден'
)

TemplateInactive = fastapi.HTTPException(
    status_code=http_status.HTTP_400_BAD_REQUEST,
    detail='Шаблон неактивен'
)

TemplateWithoutLink = fastapi.HTTPException(
    status_code=http_status.HTTP_400_BAD_REQUEST,
    detail='У шаблона не настроенна ссылка'
)