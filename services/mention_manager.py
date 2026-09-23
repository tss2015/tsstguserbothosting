from telethon.tl.types import InputUser

def mention(user) -> str:
    # Markdown-free mention using Telegram text entities is safer for
    # usernames containing unusual characters.
    name = user.first_name or user.username or "user"
    return f"[{name}](tg://user?id={user.id})"

def batches(items, size=5):
    for i in range(0, len(items), size):
        yield items[i:i+size]
