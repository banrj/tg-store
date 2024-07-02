#!/bin/bash

echo "https://api.telegram.org/bot$1/setWebhook"

curl \
  --request POST \
  --url "https://api.telegram.org/bot$1/setWebhook" \
  --header 'content-type: application/json' \
  --data '{"url": "https://d5d6goq6did08enqmi0a.apigw.yandexcloud.net/tg-webhook"'