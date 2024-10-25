import os

import uvicorn
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import settings
from app.db import utils as db_utils

from app.routes import (
    user as user_routes,
    auth as auth_routes,
    shop as shop_routes,
    products as products_routes,
    template as template_routes,
    product_categories as product_categories_routes,
    product_variants as product_variants_routes,
    product_extra_kits as product_extra_kits_routes,
    delivery_self_pickup as delivery_self_pickup_routes,
    delivery_manual as delivery_manual_routes,
    infopages_rubrics as infopages_rubrics_routes,
    infopages_posts as infopages_posts_routes,)

from app.routes.external_v1 import (
    template as external_template_routes,
    product_categories as external_product_categories_routes,
    shop as external_shop_routes)


def create_app():
    app = FastAPI(title=f'TG-Store MVP ({os.getenv("MODE")})')

    # Swagger для template API
    template_app = FastAPI(title=f'TG-Store MVP ({os.getenv("MODE")}) Template API')

    origins = [
        "http://localhost",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_routes.router)
    app.include_router(user_routes.router)
    app.include_router(shop_routes.router)
    app.include_router(template_routes.router)
    app.include_router(product_categories_routes.router)
    app.include_router(products_routes.router)
    app.include_router(product_variants_routes.router)
    app.include_router(product_extra_kits_routes.router)
    app.include_router(delivery_self_pickup_routes.router)
    app.include_router(delivery_manual_routes.router)
    app.include_router(infopages_rubrics_routes.router)
    app.include_router(infopages_posts_routes.router)

    # Тут добавляем роуты для Template API
    template_app.include_router(external_template_routes.router)
    template_app.include_router(external_product_categories_routes.router)
    template_app.include_router(external_shop_routes.router)

    app.mount("/template", template_app)

    @app.exception_handler(HTTPException)
    def handling_exc(request: Request, exc: HTTPException):
        return JSONResponse(content=exc.detail, status_code=exc.status_code)

    return app


app = create_app()


if __name__ == '__main__':
    if settings.TABLE_SUFFIX == 'localdev':
        db_utils.init_local_db_test_table(table_suffix=settings.TABLE_SUFFIX)
    uvicorn.run('app.main:app', host='0.0.0.0', port=settings.PORT, reload=True, proxy_headers=False)
