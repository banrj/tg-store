import requests
from app.config import settings


TG_TOKEN = settings.TG_KEY
WEBHOOK_URL = 'https://d5d6goq6did08enqmi0a.apigw.yandexcloud.net/tgwebhook'

method = 'setWebhook'
# method = 'deleteWebhook'
# method = 'getWebhookInfo'

url = 'https://api.telegram.org/bot{token}/{method}'.format(token=TG_TOKEN, method=method)

data = {'url': WEBHOOK_URL}


def set_webhook():
    r = requests.post(url, data)
    print(r.json())


if __name__ == '__main__':
    set_webhook()
