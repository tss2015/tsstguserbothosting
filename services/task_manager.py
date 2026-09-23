import asyncio
from dataclasses import dataclass, field

@dataclass
class UserTask:
    task_id: str
    bot_user_id: int
    chat_id: int
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
    task: asyncio.Task | None = None

class TaskManager:
    def __init__(self):
        self.tasks = {}

    def add(self, item: UserTask):
        self.tasks[item.bot_user_id] = item

    def get(self, bot_user_id):
        return self.tasks.get(bot_user_id)

    def cancel(self, bot_user_id):
        item = self.get(bot_user_id)
        if item:
            item.cancel_event.set()
            return True
        return False

    def remove(self, bot_user_id):
        self.tasks.pop(bot_user_id, None)

task_manager = TaskManager()
