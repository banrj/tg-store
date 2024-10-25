import fastapi
from fastapi import status as http_status


WrongPost = fastapi.HTTPException(
    status_code=http_status.HTTP_409_CONFLICT,
    detail='Указан неверный информационный пост.'
)

PostNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Запрашиваемой информационный пост не существует!'
)
