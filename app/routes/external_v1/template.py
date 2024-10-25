import fastapi

from app.dto import (
    template as template_dto
)
from app.handlers.external_v1.template import handle_get_template_redirect
from app.handlers.template import handle_get_template

router = fastapi.APIRouter(prefix="/templates", tags=['Template'])


# TODO добавить проверку API KEY
@router.get(
    path='/redirect/{shop_uuid}', response_model=None, tags=['Template'])
def get_template_redirect(shop_uuid: str,
                          request: fastapi.Request
                          ):
    """
        Получаем редирект на шаблон
    """
    res = request
    print(res.url)
    print(res.cookies)
    print(res.headers)
    print(res.cookies.get('session_id'))
    print(request.client.host)
    print(request.client.port)
    return handle_get_template_redirect(shop_uuid=shop_uuid)


# TODO добавить проверку API KEY
@router.get(
    path='/{template_uuid}',
    response_model=template_dto.Template,
    tags=['Template']
)
def get_template(template_uuid: str
                 ):
    """
    Информация по шаблону
    """
    return handle_get_template(template_uuid)
