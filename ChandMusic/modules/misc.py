cat > ChandMusic/modules/misc.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import config
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from ChandMusic import bot
from ChandMusic.modules.block import user_allowed

SOURCE_URL = "https://github.com/Chand/ChandMusic"


@bot.on_message(filters.command("repo") & user_allowed)
async def repo_cmd(_, message: Message) -> None:
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🍡 sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ 🍡", url=SOURCE_URL),
            InlineKeyboardButton("🔱 ғᴏʀᴋ 🔱", url=f"{SOURCE_URL}/fork"),
        ],
        [
            InlineKeyboardButton("🍬 sᴜᴘᴘᴏʀᴛ 🍬", url=config.SUPPORT_GROUP),
            InlineKeyboardButton("🍹 ᴜᴘᴅᴀᴛᴇs 🍹", url=config.UPDATES_CHANNEL),
        ],
    ])

    await message.reply(
        "╔══════════════════════════════════════════╗\n"
        "║    🍡 ᴄʜᴀɴᴅ ᴍᴜsɪᴄ sᴏᴜʀᴄᴇ          ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ ᴏᴘᴇɴ sᴏᴜʀᴄᴇ ᴍᴜsɪᴄ ʙᴏᴛ\n"
        "✦ ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ ᴄʜᴀɴᴅ ❤️\n\n"
        "⚡ ʜᴏsᴛɪɴɢ sᴜᴘᴘᴏʀᴛ\n"
        "✦ ʀᴇɴᴅᴇʀ ✅\n"
        "✦ ᴋᴏʏᴇʙ ✅\n"
        "✦ ʀᴀɪʟᴡᴀʏ ✅\n"
        "✦ ғʀᴇᴇ ʜᴏsᴛɪɴɢ ⚡\n"
        "✦ sᴍᴏᴏᴛʜ ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ 🚀\n\n"
        f"✦ <a href='{SOURCE_URL}'>ɢɪᴛʜᴜʙ ʀᴇᴘᴏ</a>\n"
        "✦ ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ʜɪᴛ ⭐ ᴏɴ ɢɪᴛʜᴜʙ\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐",
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
        disable_web_page_preview=True,
    )


@bot.on_message(filters.command("id") & user_allowed)
async def id_cmd(client, message: Message) -> None:
    chat = message.chat
    your_id = message.from_user.id if message.from_user else "N/A"
    message_id = message.id
    reply = message.reply_to_message

    text = f"✦ <a href='{message.link}'>ᴍᴇssᴀɢᴇ ɪᴅ</a> : <code>{message_id}</code>\n"
    text += f"✦ <a href='tg://user?id={your_id}'>ʏᴏᴜʀ ɪᴅ</a>     : <code>{your_id}</code>\n"

    args = message.command[1:]
    if args:
        try:
            target = await client.get_users(args[0])
            target_id = target.id
            text += f"✦ <a href='tg://user?id={target_id}'>ᴜsᴇʀ ɪᴅ</a>      : <code>{target_id}</code>\n"
        except Exception:
            await message.reply(
                "⚡ User not found.",
                parse_mode=ParseMode.HTML,
            )
            return

    if chat.username:
        chat_link = f"https://t.me/{chat.username}"
    else:
        chat_link = f"tg://user?id={chat.id}"
    text += f"✦ <a href='{chat_link}'>ᴄʜᴀᴛ ɪᴅ</a>      : <code>{chat.id}</code>\n"

    if reply and not getattr(reply, "empty", True):
        if reply.from_user and not getattr(reply, "sender_chat", None):
            text += (
                f"\n✦ <a href='{reply.link}'>ʀᴇᴘʟɪᴇᴅ ᴍsɢ ɪᴅ</a> : <code>{reply.id}</code>\n"
                f"✦ <a href='tg://user?id={reply.from_user.id}'>ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ</a>    : <code>{reply.from_user.id}</code>\n"
            )

        if getattr(reply, "forward_from_chat", None):
            fwd = reply.forward_from_chat
            text += (
                f"\n✦ ғᴡᴅ ᴄʜᴀɴɴᴇʟ    : {fwd.title}\n"
                f"✦ ғᴡᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ : <code>{fwd.id}</code>\n"
            )

        if getattr(reply, "sender_chat", None):
            sc = reply.sender_chat
            text += (
                f"\n✦ sᴇɴᴅᴇʀ ᴄʜᴀᴛ    : {sc.title}\n"
                f"✦ sᴇɴᴅᴇʀ ᴄʜᴀᴛ ɪᴅ : <code>{sc.id}</code>\n"
            )

    await message.reply(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
EOF
