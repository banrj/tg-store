# Система отзывов (back)

## :gear: Как завести проект

:snake: Поставить python 3.11  

В корне проекта:

- `python3.11 -m venv .venv`
- `source .venv/bin/activate (Linux)`  
- `.venv\Scripts\activate (Windows)`
- `pip install -r requirements.txt`
- `pip install -r requirements-test.txt`  

### :desktop_computer: Для работы приложения понадобятся переменные окружения
Подключение к базе данных
- `YC_DATABASE_URL`
- `YC_SERVICE_ACCOUNT_KEY_ID` 
- `YC_SERVICE_ACCOUNT_SECRET_KEY`
- `TABLE_SUFFIX`

Подключение к сервису Авторизации
- `IAM_SERVICE_URL`
- `IAM_OWNER_UUID` 
- `IAM_USERPOOL_UUID`
- `IAM_USERPOOL_API_KEY`  

Прочее
- `PORT`  


### :scroll: Команды можно запускать в разных режимах
Имеются `.env*` файлы с заготовленными значениями переменных  
В зависимости от выбранного режима, приложение получит переменные окружения либо из файла, либо из системы

| Режим        | Источник переменных                                   |
|--------------|-------------------------------------------------------|
| `не указан`  | `.env.local-testing`                                  |
| `CICD`       | настройки workflow                                    |
| `LOCAL_DEV`  | `.env.local-development`                              |
| `DEV`        | `.env` или значения, переданные при деплое лямбды     |
| `STAGE`      | `.env` или значения, переданные при деплое лямбды |



### :desktop_computer: Поднимите локальную версию баз данных

`docker-compose up -d`

Для запуска базы данных с предустановленным DynamoDB Admin:
`docker-compose -f docker-compose-admin.yml up -d`

Доступ к DynamoDB Admin по адресу:
`http://localhost:8001/`

### :hammer: Полный прогон тестов запускается из корня

`python -m pytest --cov=./app --cov-report=html`  
##### Запуск одного теста в PyCharm:
`Run` → `Edit Configurations...` → `Add New Configuration` →  

Параметр `Working Directory:` установить до корня проекта `../tg-store-mvp-back`

### :green_circle: Запуск проекта локально для разработки

##### В командной строке: 
`MODE=LOCAL_DEV python -m app.main`
##### В PyCharm:
`Run` → `Edit Configurations...` → `Add New Configuration` →  

Параметр `Working Directory:` установить до корня проекта `../tg-store-mvp-back`  

В параметр `Environment Variables:` добавить `MODE=LOCAL_DEV`


npm install -g dynamodb-admin
https://github.com/aaronshaf/dynamodb-admin
set DYNAMO_ENDPOINT=http://localhost:9009 && dynamodb-admin