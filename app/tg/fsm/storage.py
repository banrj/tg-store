from aiogram.fsm.storage.base import BaseStorage
from datetime import datetime


class DynamoDBStorage(BaseStorage):
    def __init__(self, table):
        self.table = table

    async def close(self):
        pass

    async def wait_closed(self):
        pass

    async def set_state(self, *, chat=None, user=None, state=None, key=None):
        if state:
            state = state.state
        data = {
            'time': int(datetime.now().timestamp()),
            'bot': key.bot_id,
            'user': key.user_id,
            'state': state
            }
        async with self.table as table:
            await table.put_item(
                Item={
                    'partkey': f'state_{key.bot_id}',
                    'sortkey': f'{key.user_id}',
                    **data
                }
            )

    async def get_state(self, *, chat=None, user=None, key=None):
        async with self.table as table:
            response = await table.get_item(
                Key={
                    'partkey': f'state_{key.bot_id}',
                    'sortkey': f'{key.user_id}'
                }
            )
        item = response.get('Item')
        if item:
            return item['state']
        return None

    async def set_data(self, *, chat=None, user=None, data=None, key=None):
        async with self.table as table:
            await table.put_item(
                Item={
                    'partkey': f'data_state_{key.bot_id}',
                    'sortkey': f'{key.user_id}',
                    **data
                }
            )

    async def get_data(self, *, chat=None, user=None, default=None, key=None):
        async with self.table as table:
            response = await table.get_item(
                Key={
                    'partkey': f'data_state_{key.bot_id}',
                    'sortkey': f'{key.user_id}',
                }
            )
        item = response.get('Item')
        if item:
            return item
        return default or {}

    async def update_data(self, *, chat=None, user=None, data=None, key,  **kwargs):
        current_data = await self.get_data(chat=chat, user=user, key=key, default={})
        if not isinstance(current_data, dict):
            current_data = {}
        current_data.update(data or {})
        await self.set_data(chat=chat, user=user, data=current_data, key=key)
        return current_data

    async def reset_state_data(self, *, chat=None, user=None, key=None):
        async with self.table as table:
            await table.delete_item(
                Key={
                    'partkey': f'state_data_{key.bot_id}',
                    'sortkey': f'{key.user_id}'
                }
            )
