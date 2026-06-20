cat > ChandMusic/modules/stop.py << 'EOF'
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

from ChandMusic import bot
from ChandMusic.core.call import leave_vc
from ChandMusic.core.queue import clear_queue, queue_size
from ChandMusic.modules.block import group_allowed, user_allowed
from ChandMusic.utils.permissions import is_user_authorized


@bot.on_message(
    filters.group
    & filters.command(["stop", "end"])
    & group_allowed
    & user_allowed
)
async def stop_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply(
            "⚡ ᴀᴅᴍɪɴ ᴏɴʟʏ",
            parse_mode=ParseMode.HTML,
        )
        return

    await leave_vc(message.chat.id)
    await message.reply(
        "⏹️ ᴘʟᴀʏʙᴀᴄᴋ ꜱᴛᴏᴘᴘᴇᴅ\n"
        "✅ Qᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ\n"
        "✦ ʟᴇꜰᴛ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(
    filters.group
    & filters.command("clear")
    & group_allowed
    & user_allowed
)
async def clear_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply(
            "⚡ ᴀᴅᴍɪɴ ᴏɴʟʏ",
            parse_mode=ParseMode.HTML,
        )
        return

    chat_id = message.chat.id

    try:
        from ChandMusic.core.autoplay import stop_autoplay
        stop_autoplay(chat_id)
    except Exception:
        pass

    if not queue_size(chat_id):
        await message.reply(
            "⚡ Qᴜᴇᴜᴇ ɪꜱ ᴇᴍᴘᴛʏ",
            parse_mode=ParseMode.HTML,
        )
        return

    clear_queue(chat_id)
    await message.reply(
        "✅ Qᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ\n"
        "✦ ᴀʟʟ ꜱᴏɴɢꜱ ʀᴇᴍᴏᴠᴇᴅ",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(
    filters.group
    & filters.command("reboot")
    & group_allowed
    & user_allowed
)
async def reboot_cmd(_, message: Message) -> None:
    await leave_vc(message.chat.id)
    await message.reply(
        "🔄 ᴄʜᴀᴛ ʀᴇʙᴏᴏᴛᴇᴅ\n"
        "✦ ᴀʟʟ ꜱᴛᴀᴛᴇꜱ ʀᴇꜱᴇᴛ",
        parse_mode=ParseMode.HTML,
    )
EOF
