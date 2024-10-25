import fastapi
from fastapi import status as http_status


TokenExpired = fastapi.HTTPException(
    status_code=http_status.HTTP_401_UNAUTHORIZED,
    detail='Токен просрочен'
)

TokenInvalid = fastapi.HTTPException(
    status_code=http_status.HTTP_401_UNAUTHORIZED,
    detail='Токен некорректный'
)

TokenWrongType = lambda t: fastapi.HTTPException(
    status_code=http_status.HTTP_401_UNAUTHORIZED,
    detail=f'Токен не того типа (надо {t})'
)

MissedJTI = fastapi.HTTPException(
    status_code=http_status.HTTP_401_UNAUTHORIZED,
    detail='Отсутствует JTI'
)

TokenBlacklisted = fastapi.HTTPException(
    status_code=http_status.HTTP_403_FORBIDDEN,
    detail='Токен в черном списке'
)

MissedSub = fastapi.HTTPException(
    status_code=http_status.HTTP_403_FORBIDDEN,
    detail='Отсутствует SUB'
)

WrongApiKey = fastapi.HTTPException(
    status_code=http_status.HTTP_403_FORBIDDEN,
    detail='Неправильный API ключ'
)
