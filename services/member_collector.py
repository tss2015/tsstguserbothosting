from telethon.tl.types import User

async def eligible_members(client, chat):
    result = []
    async for user in client.iter_participants(chat):
        if not isinstance(user, User):
            continue
        if user.bot or user.deleted:
            continue
        if user.is_self:
            continue
        result.append(user)
    return result
