import logging
import fastapi

from app.dto import (
    user as user_dto,
)
from app.handlers import (
    user as user_handlers,
    auth as auth_handlers
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/user", tags=['User'])


@router.get(
    path='/me',
    response_model=user_dto.User,
    response_model_exclude={'partkey', 'sortkey'}
)
def get_me(
    auth_data: user_dto.AuthData = fastapi.Depends(auth_handlers.auth_user)
):
    """

    """
    return auth_data.user


@router.patch(
    path='/details',
    response_model=user_dto.User
)
def update_details(
    details: user_dto.UserDetails,
    auth_data: user_dto.AuthData = fastapi.Depends(auth_handlers.auth_user)
):
    """
    Обновление деталей пользователя
    """
    return user_handlers.handle_update_details(
        user=auth_data.user,
        details=details,
    ).to_ui()
