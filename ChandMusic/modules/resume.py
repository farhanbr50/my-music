cat > ChandMusic/modules/resume.py << 'EOF'
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

from ChandMusic import bot, call_py
from ChandMusic.modules.block import group_allowed, user_allowed
from ChandMusic.utils.permissions import is_user_authorized


@bot.on_message(
    filters.group
    & filters.command("resume")
    & group_allowed
    & user_allowed
)
async def resume_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply(
            "⚡ ᴀᴅᴍɪɴ ᴏɴʟʏ\n"
            "✦ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ғᴏʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs.",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await call_py.resume(message.chat.id)
        await message.reply(
            "▶️ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ\n"
            "✦ ᴍᴜsɪᴄ ᴘʟᴀʏʙᴀᴄᴋ ᴄᴏɴᴛɪɴᴜᴇᴅ.",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply(
            f"⚡ ʀᴇsᴜᴍᴇ ғᴀɪʟᴇᴅ\n<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
EOF
