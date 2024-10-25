import fastapi
from fastapi import status as http_status

from app import settings

InvalidTGAuthData = fastapi.HTTPException(
    status_code=http_status.HTTP_400_BAD_REQUEST,
    detail="Invalid Telegram auth data!"
)

UserNotFound = fastapi.HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND,
    detail='Пользователь не найден'
)

BackupFrequency = fastapi.HTTPException(
    status_code=http_status.HTTP_400_BAD_REQUEST,
    detail=f'Бекап можно делать раз в {settings.BACKUP_DELAY_IN_DAYS} дней'
)
