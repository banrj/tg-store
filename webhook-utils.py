import requests
from app.config import settings


TG_TOKEN = settings.TG_KEY
WEBHOOK_URL = settings.WEBHOOK

url = 'https://api.telegram.org/bot{token}/setWebhook'.format(token=TG_TOKEN)

data = {'url': WEBHOOK_URL}


def set_webhook():
    r = requests.post(url, data)
    print(r.json())


if __name__ == '__main__':
    set_webhook()
