cat > ChandMusic/modules/autoplay.py << 'EOF'
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

from ChandMusic import bot
from ChandMusic.core.autoplay import get_autoplay_query, is_autoplay, start_autoplay, stop_autoplay
from ChandMusic.core.call import leave_vc
from ChandMusic.core.player import play_song
from ChandMusic.core.queue import peek_current, queue_size
from ChandMusic.modules.block import group_allowed, user_allowed
from ChandMusic.utils.formatters import short
from ChandMusic.utils.permissions import is_user_authorized


@bot.on_message(
    filters.group
    & filters.regex(r"^/autoplay(?:@\w+)?(?:\s+(?P<q>.+))?$")
    & group_allowed
    & user_allowed
)
async def autoplay_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    user = message.from_user

    if not await is_user_authorized(message):
        await message.reply(
            "⚡ ᴀᴅᴍɪɴ ᴏɴʟʏ\n"
            "✦ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ /autoplay",
            parse_mode=ParseMode.HTML,
        )
        return

    match = message.matches[0]
    query = (match.group("q") or "").strip()

    if not query:
        current_q = get_autoplay_query(chat_id)
        if is_autoplay(chat_id) and current_q:
            await message.reply(
                f"🔁 ᴀᴜᴛᴏᴘʟᴀʏ ɪꜱ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ\n"
                f"✦ Qᴜᴇʀʏ : <code>{current_q}</code>\n"
                f"✦ ᴜꜱᴇ /end ᴛᴏ ꜱᴛᴏᴘ ᴀᴜᴛᴏᴘʟᴀʏ ꜰɪʀꜱᴛ",
                parse_mode=ParseMode.HTML,
            )
        else:
            await message.reply(
                "✦ ᴜꜱᴀɢᴇ : <code>/autoplay sidhu moose wala</code>\n"
                "✦ ᴛʜɪꜱ ᴡɪʟʟ ᴄᴏɴᴛɪɴᴜᴏᴜꜱʟʏ ᴘʟᴀʏ ꜱᴏɴɢꜱ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ",
                parse_mode=ParseMode.HTML,
            )
        return

    pm = await message.reply(
        f"🔁 ꜱᴇᴛᴛɪɴɢ ᴜᴘ ᴀᴜᴛᴏᴘʟᴀʏ...\n"
        f"✦ Qᴜᴇʀʏ : <code>{query}</code>",
        parse_mode=ParseMode.HTML,
    )

    req = user.first_name if user else "AutoPlay"
    req_id = user.id if user else 0

    was_playing = queue_size(chat_id) > 0
    count = await start_autoplay(chat_id, query, req, req_id)

    if count == 0:
        stop_autoplay(chat_id)
        await pm.edit_text(
            "⚡ ᴀᴜᴛᴏᴘʟᴀʏ ꜰᴀɪʟᴇᴅ\n"
            "✦ ɴᴏ ꜱᴏɴɢꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ, ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ",
            parse_mode=ParseMode.HTML,
        )
        return

    first = peek_current(chat_id)

    await pm.edit_text(
        f"🔁 ᴀᴜᴛᴏᴘʟᴀʏ ꜱᴛᴀʀᴛᴇᴅ\n"
        f"✦ Qᴜᴇʀʏ : <code>{query}</code>\n"
        f"✦ {count} ꜱᴏɴɢꜱ ᴀᴅᴅᴇᴅ ᴛᴏ Qᴜᴇᴜᴇ\n"
        f"✦ ᴜꜱᴇ /end ᴛᴏ ꜱᴛᴏᴘ ᴀᴜᴛᴏᴘʟᴀʏ",
        parse_mode=ParseMode.HTML,
    )

    if not was_playing and first:
        dm = await bot.send_message(
            chat_id,
            f"▶️ ɴᴏᴡ ᴘʟᴀʏɪɴɢ : <code>{short(first['title'])}</code>",
            parse_mode=ParseMode.HTML,
        )
        await play_song(chat_id, dm, first)

    try:
        await message.delete()
    except Exception:
        pass


@bot.on_message(
    filters.group
    & filters.command("end")
    & group_allowed
    & user_allowed
)
async def end_cmd(_, message: Message) -> None:
    chat_id = message.chat.id

    if not await is_user_authorized(message):
        await message.reply(
            "⚡ ᴀᴅᴍɪɴ ᴏɴʟʏ\n"
            "✦ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ /end",
            parse_mode=ParseMode.HTML,
        )
        return

    if not is_autoplay(chat_id):
        await message.reply(
            "⚡ ᴀᴜᴛᴏᴘʟᴀʏ ɪꜱ ɴᴏᴛ ʀᴜɴɴɪɴɢ\n"
            "✦ ᴜꜱᴇ <code>/autoplay &lt;query&gt;</code> ᴛᴏ ꜱᴛᴀʀᴛ",
            parse_mode=ParseMode.HTML,
        )
        return

    stop_autoplay(chat_id)
    await leave_vc(chat_id)

    await message.reply(
        "⏹️ ᴀᴜᴛᴏᴘʟᴀʏ ꜱᴛᴏᴘᴘᴇᴅ\n"
        "✅ ǫᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ\n"
        "✦ ʟᴇꜰᴛ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ",
        parse_mode=ParseMode.HTML,
    )
EOF
