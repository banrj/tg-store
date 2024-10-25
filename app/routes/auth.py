import logging
import fastapi

from app.dto import (
    user as user_dto,
    auth as auth_dto,
    common as dto_common
)
from app.handlers import (
    user as user_handlers
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/auth", tags=['Auth'])


@router.post(
    path='/authorize',
    response_model=auth_dto.TokenPair
)
def authorize_user(
    tg_auth_data: user_dto.TelegramAuthorizationData
):
    return user_handlers.handle_login_user(
        tg_id=tg_auth_data.id,
        first_name=tg_auth_data.first_name,
        last_name=tg_auth_data.last_name,
        username=tg_auth_data.username,
        auth_date=tg_auth_data.auth_date,
        photo_url=tg_auth_data.photo_url,
        tg_hash=tg_auth_data.hash
    )


@router.post(
    path='/token',
    response_model=auth_dto.TokenPair
)
def refresh_token(token: auth_dto.RefreshToken):

    return user_handlers.handle_refresh_token(
        token=token.refresh_token
    )


@router.post(
    path='/logout',
    response_model=dto_common.ResponseNoBody
)
def refresh_token(token: auth_dto.RefreshToken):
    user_handlers.handle_logout(token=token.refresh_token)

    return dto_common.ResponseNoBody()
