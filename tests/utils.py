import os
import io

import fastapi

from app import settings
from app.db import config as db_config, keys_structure
from app.db.utils import connect_table



def drop_general_table():
    TABLE_NAME = db_config.general_table.format(mode=settings.TABLE_SUFFIX)
    table = connect_table(TABLE_NAME)
    scan = table.scan()
    with table.batch_writer() as batch:
        for item in scan['Items']:
            batch.delete_item(
                Key={keys_structure.db_table_partkey: item['partkey'], keys_structure.db_table_sortkey: item['sortkey']}
            )


def drop_tokens_table():
    TABLE_NAME = db_config.tokens_table.format(mode=settings.TABLE_SUFFIX)
    table = connect_table(TABLE_NAME)
    scan = table.scan()
    with table.batch_writer() as batch:
        for item in scan['Items']:
            batch.delete_item(
                Key={keys_structure.db_table_partkey: item['partkey'], keys_structure.db_table_sortkey: item['sortkey']}
            )


class TestUploadFile(fastapi.UploadFile):
    def __init__(self, filename: str, file: io.BytesIO, content_type: str):
        super().__init__(filename=filename, file=file)
        self._content_type = content_type

    @property
    def content_type(self): # Override content_type
        return self._content_type


def get_image_file() -> fastapi.UploadFile:
    print("\n\nCurrent workdir is: " + os.getcwd() + "\n\n")
    contents = open("tests/utils/test.svg", "rb").read()
    return TestUploadFile(filename="test_image.svg", file=io.BytesIO(contents), content_type="image/svg+xml")
