cat > ChandMusic/modules/skip.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ChandMusic import bot, call_py
from ChandMusic.core.call import leave_vc
from ChandMusic.core.player import play_song
from ChandMusic.core.queue import peek_current, pop_current, queue_size
from ChandMusic.modules.block import group_allowed, user_allowed
from ChandMusic.utils.formatters import short
from ChandMusic.utils.helpers import delete_file
from ChandMusic.utils.permissions import is_user_authorized


@bot.on_message(
    filters.group
    & filters.command("skip")
    & group_allowed
    & user_allowed
)
async def skip_cmd(_, message: Message) -> None:
    chat_id = message.chat.id

    if not await is_user_authorized(message):
        await message.reply(
            "⚡ ᴀᴅᴍɪɴ ᴏɴʟʏ\n"
            "✦ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ғᴏʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs.",
            parse_mode=ParseMode.HTML,
        )
        return

    if not queue_size(chat_id):
        await message.reply(
            "⚡ ǫᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ\n"
            "✦ ɴᴏ sᴏɴɢs ᴛᴏ sᴋɪᴘ.",
            parse_mode=ParseMode.HTML,
        )
        return

    sm = await message.reply(
        "✦ sᴋɪᴘᴘɪɴɢ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ...",
        parse_mode=ParseMode.HTML,
    )

    skipped = pop_current(chat_id)

    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass

    await asyncio.sleep(2)

    try:
        delete_file(skipped.get("file_path", ""))
    except Exception:
        pass

    nxt = peek_current(chat_id)

    if nxt:
        await sm.edit_text(
            f"⏭️ sᴋɪᴘᴘᴇᴅ ᴛʀᴀᴄᴋ : <code>{short(skipped['title'])}</code>\n"
            f"▶️ ɴᴏᴡ ᴘʟᴀʏɪɴɢ :\n<code>{nxt['title']}</code>",
            parse_mode=ParseMode.HTML,
        )
        dm = await bot.send_message(
            chat_id,
            f"🎵 ɴᴇxᴛ ᴛʀᴀᴄᴋ : <code>{nxt['title']}</code>",
            parse_mode=ParseMode.HTML,
        )
        await play_song(chat_id, dm, nxt)
    else:
        await sm.edit_text(
            f"⏭️ sᴋɪᴘᴘᴇᴅ ᴛʀᴀᴄᴋ : <code>{short(skipped['title'])}</code>\n"
            "⚡ ǫᴜᴇᴜᴇ ɪs ɴᴏᴡ ᴇᴍᴘᴛʏ",
            parse_mode=ParseMode.HTML,
        )
EOF
