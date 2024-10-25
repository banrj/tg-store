import logging
import fastapi

from app.dto import (
    template as template_dto,
    common as dto_common,
    user as user_dto
)
from app.handlers import template as tepmlate_handlers, auth as auth_handlers

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/templates", tags=['Template'])


@router.post(
    path='',
    response_model=template_dto.Template,
    dependencies=[fastapi.Depends(auth_handlers.admin_custom_headers), fastapi.Depends(auth_handlers.check_admin_key)]
)
def add_template(
        data: template_dto.TemplateRequestBody = fastapi.Body(...),
        photo: fastapi.UploadFile = fastapi.File(...)
):
    """
    Добавить шаблон. Пока нет ролевой системы с админами, работает в ручном режиме.
    """
    return tepmlate_handlers.handle_add_template(data=data, photo=photo)


@router.patch(
    path='/{template_uuid}',
    response_model=template_dto.Template,
    dependencies=[fastapi.Depends(auth_handlers.admin_custom_headers), fastapi.Depends(auth_handlers.check_admin_key)]
)
def update_template(
        template_uuid: dto_common.UUIDasStr,
        data: template_dto.TemplateUpdateBody = fastapi.Body(None),
        photo: fastapi.UploadFile | str = fastapi.File(None)
):
    """
    Изменить запись шаблона. Пока нет ролевой системы с админами, работает в ручном режиме.
    """
    return tepmlate_handlers.handle_update_template(template_uuid=template_uuid, data=data, photo=photo)


@router.get(
    path='',
    response_model=list[template_dto.Template]
)
def get_list_templates(auth_data: user_dto.AuthData = fastapi.Depends(auth_handlers.auth_user)):
    """
    Список добавленных шаблонов
    """
    return tepmlate_handlers.handle_get_list_templates()


@router.get(
    path='/{template_uuid}',
    response_model=template_dto.Template
)
def get_template(template_uuid: str, auth_data: user_dto.AuthData = fastapi.Depends(auth_handlers.auth_user)):
    """
    Информация по шаблону
    """
    return tepmlate_handlers.handle_get_template(template_uuid)


@router.delete(
    path='/{template_uuid}',
    response_model=template_dto.Template,
    dependencies=[fastapi.Depends(auth_handlers.admin_custom_headers), fastapi.Depends(auth_handlers.check_admin_key)]
)
def delete_template(template_uuid: dto_common.UUIDasStr):
    """
    Сделать шаблон неактивным.
    """
    return tepmlate_handlers.handle_delete_template(template_uuid=template_uuid)
