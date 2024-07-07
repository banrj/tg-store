from app.main import create_app as create_fastapi_app
from app.yc.dispatcher import Dispatcher

fastapi_application = create_fastapi_app()

handle = Dispatcher(fastapi_application)
