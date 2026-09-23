from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.tasks = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
        await self.client.admin.command("ping")
        self.db = self.client[settings.database_name]
        self.users = self.db.users
        self.tasks = self.db.tasks
        await self.users.create_index("bot_user_id", unique=True)
        await self.tasks.create_index([("bot_user_id", 1), ("created_at", -1)])

    async def close(self):
        if self.client:
            self.client.close()

db = Database()
