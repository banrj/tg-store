from app.main import create_app
from app.yc.dispatcher import Dispatcher

function_app = create_app()

handler = Dispatcher(function_app)
