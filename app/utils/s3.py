import fastapi
import boto3
from botocore.config import Config

from app import settings


def bucket_client():
    s3 = boto3.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=settings.YC_SERVICE_ACCOUNT_KEY_ID,
        aws_secret_access_key=settings.YC_SERVICE_ACCOUNT_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='ru-central1'  # укажите ваш регион, если необходимо
    )
    return s3


def bucket_resource():
    s3 = boto3.resource(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=settings.YC_SERVICE_ACCOUNT_KEY_ID,
        aws_secret_access_key=settings.YC_SERVICE_ACCOUNT_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='ru-central1'  # укажите ваш регион, если необходимо
    )
    return s3


def upload_file_to_s3(bucket_name: str, bucket_url: str, file: fastapi.UploadFile, content_type: str = None):
    s3_client = bucket_client()
    return s3_client.upload_fileobj(
        Fileobj=file.file,
        Bucket=bucket_name,
        Key=bucket_url,
        ExtraArgs={"ContentType": file.content_type or content_type}
    )


def delete_files_from_s3(bucket_name: str, files: list[dict]):
    s3_resource = bucket_resource()
    return s3_resource.meta.client.delete_objects(
        Bucket=bucket_name,
        Delete={'Objects': files}
    )


def delete_different_images_from_s3(current_urls, new_urls):
    diff_urls = set(current_urls) - set(new_urls)
    s3_names = [{'Key': str(img).split("/", 4)[-1]} for img in diff_urls]
    if bool(s3_names):
        delete_files_from_s3(bucket_name=settings.YC_PRODUCTS_BUCKET_NAME, files=s3_names)


def delete_image_from_s3(image_url):
    delete_files_from_s3(
        bucket_name=settings.YC_PRODUCTS_BUCKET_NAME,
        files=[{'Key': str(image_url).split("/", 4)[-1]}]
    )
