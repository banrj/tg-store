import logging
from typing import List

import fastapi

from app.dto import (
    infopages_posts as dto_infopages_posts,
    common as dto_common,
    user as dto_user
)
from app.handlers import (
    auth as handlers_auth, infopages_posts as handlers_infopages_posts
)

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/infopages/posts", tags=['Info Pages Posts'])


@router.post(
    path='/{owner_uuid}/{shop_uuid}',
    response_model=dto_infopages_posts.Post,
)
def add_infopages_post(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        data: dto_infopages_posts.PostCreateRequest = fastapi.Body(None),
        images: List[fastapi.UploadFile] = fastapi.File(None),
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Добавить информационный пост.
    """
    return handlers_infopages_posts.handle_create_rubric(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        data=data,
        images=images,
    )


@router.patch(
    path='/{owner_uuid}/{shop_uuid}/{post_uuid}',
    response_model=dto_infopages_posts.Post,
)
def update_infopages_post(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        post_uuid: dto_common.UUIDasStr,
        data: dto_infopages_posts.PostUpdateRequest = fastapi.Body(None),
        images: List[fastapi.UploadFile] = fastapi.File(None),
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Изменить информационный пост.
    """
    return handlers_infopages_posts.handle_update_post(
        user_uuid=auth_data.user.uuid_,
        owner_uuid=owner_uuid,
        shop_uuid=shop_uuid,
        post_uuid=post_uuid,
        data=data,
        images=images,
    )


@router.get(
    path='/{shop_uuid}/{post_uuid}',
    response_model=dto_infopages_posts.Post,
)
def get_infopages_post(
        shop_uuid: dto_common.UUIDasStr,
        post_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить информационный пост.
    """
    return handlers_infopages_posts.handle_get_post(
        shop_uuid=shop_uuid,
        post_uuid=post_uuid,
    )


@router.get(
    path='/list/by/{shop_uuid}/',
    response_model=list[dto_infopages_posts.Post],
)
def get_list_of_shop_infopages_posts(
        shop_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить все посты для магазина без учета рубрики.
    """
    return handlers_infopages_posts.handle_get_shop_posts_list(
        shop_uuid=shop_uuid,
    )


@router.get(
    path='/list/by/{shop_uuid}/{rubric_uuid}',
    response_model=list[dto_infopages_posts.Post],
)
def get_list_of_shop_infopages_posts(
        shop_uuid: dto_common.UUIDasStr,
        rubric_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Получить все посты определенной рубрики.
    """
    return handlers_infopages_posts.handle_get_rubric_posts_list(
        shop_uuid=shop_uuid,
        rubric_uuid=rubric_uuid,
    )


@router.delete(
    path='/{owner_uuid}/{shop_uuid}/{post_uuid}',
    response_model=dto_common.ResponseNoBody,
)
def make_inactive_infopages_post(
        owner_uuid: dto_common.UUIDasStr,
        shop_uuid: dto_common.UUIDasStr,
        post_uuid: dto_common.UUIDasStr,
        auth_data: dto_user.AuthData = fastapi.Depends(handlers_auth.auth_user),
):
    """
    Удалить (сделать неактивным) информационный пост.
    """
    return handlers_infopages_posts.handle_delete_post(
        user_uuid=auth_data.user.uuid_,
        shop_uuid=shop_uuid,
        post_uuid=post_uuid,
    )
