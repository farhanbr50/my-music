cat > ChandMusic/modules/block.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ChandMusic import bot
from ChandMusic.utils.db import (
    block_group,
    unblock_group,
    is_group_blocked,
    get_blocked_groups,
    block_user,
    unblock_user,
    is_user_blocked_db,
    get_blocked_users,
)


def _group_not_blocked(_, __, message: Message) -> bool:
    if message.chat and message.chat.id:
        return not is_group_blocked(message.chat.id)
    return True


def _user_not_blocked(_, __, message: Message) -> bool:
    if message.from_user and message.from_user.id:
        return not is_user_blocked_db(message.from_user.id)
    return True


group_allowed = filters.create(_group_not_blocked)
user_allowed = filters.create(_user_not_blocked)


@bot.on_message(filters.command("gblock") & filters.user(config.OWNER_ID))
async def gblock_cmd(_, message: Message) -> None:
    args = message.command[1:]

    if args:
        try:
            chat_id = int(args[0])
        except ValueError:
            await message.reply(
                "⚡ Invalid chat ID.\n"
                "✦ Usage: /gblock -100xxxxxxx",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        if message.chat.type.name == "PRIVATE":
            await message.reply(
                "⚡ Use in a group or provide a chat ID.\n"
                "✦ Usage: /gblock -100xxxxxxx",
                parse_mode=ParseMode.HTML,
            )
            return
        chat_id = message.chat.id

    if is_group_blocked(chat_id):
        await message.reply(
            f"⚡ Chat already blocked.\n"
            f"✦ ID: <code>{chat_id}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    block_group(chat_id)
    await message.reply(
        f"✅ Chat blocked ✅\n"
        f"✦ ID: <code>{chat_id}</code>\n"
        f"✦ No commands will work in this chat.",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(filters.command("gunblock") & filters.user(config.OWNER_ID))
async def gunblock_cmd(_, message: Message) -> None:
    args = message.command[1:]

    if args:
        try:
            chat_id = int(args[0])
        except ValueError:
            await message.reply(
                "⚡ Invalid chat ID.\n"
                "✦ Usage: /gunblock -100xxxxxxx",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        if message.chat.type.name == "PRIVATE":
            await message.reply(
                "⚡ Use in a group or provide a chat ID.\n"
                "✦ Usage: /gunblock -100xxxxxxx",
                parse_mode=ParseMode.HTML,
            )
            return
        chat_id = message.chat.id

    if not is_group_blocked(chat_id):
        await message.reply(
            f"⚡ Chat is not blocked.\n"
            f"✦ ID: <code>{chat_id}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    unblock_group(chat_id)
    await message.reply(
        f"✅ Chat unblocked ✅\n"
        f"✦ ID: <code>{chat_id}</code>",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(filters.command("blocklist") & filters.user(config.OWNER_ID))
async def blocklist_cmd(_, message: Message) -> None:
    chats = get_blocked_groups()

    if not chats:
        await message.reply(
            "⚡ No blocked chats found.",
            parse_mode=ParseMode.HTML,
        )
        return

    lines = "\n".join(f"• <code>{c}</code>" for c in chats)
    await message.reply(
        f"🚫 Blocked Chats:\n{lines}",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(filters.command("ublock") & filters.user(config.OWNER_ID))
async def ublock_cmd(_, message: Message) -> None:
    args = message.command[1:]

    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    elif args:
        try:
            user_id = int(args[0])
        except ValueError:
            await message.reply(
                "⚡ Invalid user ID.\n"
                "✦ Usage: /ublock &lt;user_id&gt;",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        await message.reply(
            "⚡ Reply to a user or provide an ID.\n"
            "✦ Usage: /ublock &lt;user_id&gt;",
            parse_mode=ParseMode.HTML,
        )
        return

    if is_user_blocked_db(user_id):
        await message.reply(
            f"⚡ User already blocked.\n"
            f"✦ ID: <code>{user_id}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    block_user(user_id)
    await message.reply(
        f"✅ User blocked ✅\n"
        f"✦ ID: <code>{user_id}</code>",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(filters.command("unblock") & filters.user(config.OWNER_ID))
async def unblock_cmd(_, message: Message) -> None:
    args = message.command[1:]

    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    elif args:
        try:
            user_id = int(args[0])
        except ValueError:
            await message.reply(
                "⚡ Invalid user ID.\n"
                "✦ Usage: /unblock &lt;user_id&gt;",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        await message.reply(
            "⚡ Reply to a user or provide an ID.\n"
            "✦ Usage: /unblock &lt;user_id&gt;",
            parse_mode=ParseMode.HTML,
        )
        return

    if not is_user_blocked_db(user_id):
        await message.reply(
            f"⚡ User is not blocked.\n"
            f"✦ ID: <code>{user_id}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    unblock_user(user_id)
    await message.reply(
        f"✅ User unblocked ✅\n"
        f"✦ ID: <code>{user_id}</code>",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(filters.command("userlist") & filters.user(config.OWNER_ID))
async def userlist_cmd(_, message: Message) -> None:
    users = get_blocked_users()

    if not users:
        await message.reply(
            "⚡ No blocked users found.",
            parse_mode=ParseMode.HTML,
        )
        return

    lines = "\n".join(f"• <code>{u}</code>" for u in users)
    await message.reply(
        f"🚫 Blocked Users:\n{lines}",
        parse_mode=ParseMode.HTML,
    )
EOF
