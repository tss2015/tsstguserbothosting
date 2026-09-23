import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError

class TelegramClientManager:
    def __init__(self):
        self.clients = {}
        self.locks = {}

    def lock_for(self, bot_user_id):
        return self.locks.setdefault(bot_user_id, asyncio.Lock())

    async def disconnect(self, bot_user_id):
        client = self.clients.pop(bot_user_id, None)
        if client:
            await client.disconnect()

    async def connect_session(self, bot_user_id, session_string, api_id, api_hash):
        client = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash,
        )
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            raise ValueError("Session is not authorized.")
        self.clients[bot_user_id] = client
        return client

manager = TelegramClientManager()

# Imported lazily to keep the module easy to test.
from telethon.sessions import StringSession
