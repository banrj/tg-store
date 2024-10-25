import logging

import fastapi

from app.dto import (
    infopages_rubrics as dto_infopages_rubrics,
    common as dto_common,
    user as user_dto
)
from app.handlers import infopages_rubrics as handlers_infopages_rubrics, auth as handlers_auth


logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/infopages/rubrics", tags=['Info Pages Rubrics'])


@router.post(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_infopages_rubrics.Rubric,
)
def add_infopages_rubric(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        data: dto_infopages_rubrics.RubricCreateRequest = fastapi.Body(...),
        image: fastapi.UploadFile | str = fastapi.File(None),
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить рубрику информационных страниц.
    """
    return handlers_infopages_rubrics.handle_create_rubric(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        data=data,
        image=image,
    )


@router.patch(
    path='/{owner_uuid}/{shop_uuid}/{rubric_uuid}',
    response_model=dto_infopages_rubrics.Rubric,
)
def update_infopages_rubric(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        rubric_uuid: dto_common.UUIDasStr,
        data: dto_infopages_rubrics.RubricUpdateRequest = fastapi.Body(None),
        image: fastapi.UploadFile | str = fastapi.File(None),
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить рубрику информационных страниц.
    """
    return handlers_infopages_rubrics.handle_update_rubric(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        rubric_uuid=rubric_uuid,
        data=data,
        image=image,
    )


@router.get(
    path='/{shop_uuid}',
    response_model=list[dto_infopages_rubrics.Rubric],
)
def get_infopages_rubrics_list(
        shop_uuid: dto_common.UUIDasStr,
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить список рубрик информационных страниц.
    """
    return handlers_infopages_rubrics.handle_get_rubrics_list(shop_uuid=shop_uuid)


@router.get(
    path='/{shop_uuid}/{rubric_uuid}',
    response_model=dto_infopages_rubrics.Rubric,
)
def get_infopages_rubric(
        shop_uuid: dto_common.UUIDasStr,
        rubric_uuid: dto_common.UUIDasStr,
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить информацию о рубрике информационных страниц.
    """
    return handlers_infopages_rubrics.handle_get_rubric(shop_uuid=shop_uuid, rubric_uuid=rubric_uuid)


@router.delete(path='/{shop_uuid}/{rubric_uuid}', response_model=dto_common.ResponseNoBody)
def delete_infopages_rubric(
        shop_uuid: dto_common.UUIDasStr,
        rubric_uuid: dto_common.UUIDasStr,
        auth_data: user_dto.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Удалить (сделать неактивной) рубрику информационных страниц.
    """
    return handlers_infopages_rubrics.handle_delete_rubric(
        user_uuid=auth_data.user.uuid_, shop_uuid=shop_uuid, rubric_uuid=rubric_uuid)
