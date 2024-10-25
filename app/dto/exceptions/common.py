import fastapi
from fastapi import status as http_status

NoUpdateData = fastapi.HTTPException(
    status_code=http_status.HTTP_400_BAD_REQUEST,
    detail='Нет данных для обновления!'
)


IncorrectOwner = fastapi.HTTPException(
    status_code=http_status.HTTP_403_FORBIDDEN,
    detail='Изменять статус активности данной сущности может только ее владелец!'
)
