cat > ChandMusic/modules/play.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import re
import time

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ChandMusic import bot, call_py
from ChandMusic.core.player import play_song
from ChandMusic.core.queue import add_to_queue, peek_current, queue_size
from ChandMusic.modules.block import group_allowed, user_allowed
from ChandMusic.utils.assistant import is_assistant_in, try_join_assistant
from ChandMusic.utils.formatters import iso_to_human, parse_dur, short
from ChandMusic.utils.youtube import search_yt

_last_cmd: dict[int, float] = {}
_pending: dict[int, tuple] = {}

BLOCKED_WORDS = ["xxx", "porn", "adult"]


async def _run_pending(chat_id: int, wait: int) -> None:
    await asyncio.sleep(wait)
    if chat_id in _pending:
        _, rep = _pending.pop(chat_id)
        try:
            await rep.delete()
        except Exception:
            pass


@bot.on_message(
    filters.group
    & filters.regex(r"^/(?P<cmd>v?play)(?:@\w+)?(?:\s+(?P<q>.+))?$")
    & group_allowed
    & user_allowed
)
async def play_handler(_, message: Message) -> None:
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0

    match = message.matches[0]
    query = (match.group("q") or "").strip()
    cmd = (match.group("cmd") or "play").strip()

    try:
        await message.delete()
    except Exception:
        pass

    if not query:
        await bot.send_message(
            chat_id,
            "✦ ᴜsᴀɢᴇ : <code>/play song name</code>\n"
            "✦ ᴏʀ : <code>/play youtube url</code>\n"
            "✦ ᴠɪᴅᴇᴏ : <code>/vplay song name</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    pm = await message.reply(
        "✦ ᴘʀᴏᴄᴇssɪɴɢ...",
        parse_mode=ParseMode.HTML,
    )

    status = await is_assistant_in(chat_id)
    if status == "banned":
        await pm.edit_text(
            "⚡ ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ\n"
            "✦ ᴘʟᴇᴀsᴇ ᴜɴʙᴀɴ ᴀssɪsᴛᴀɴᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ",
            parse_mode=ParseMode.HTML,
        )
        return

    if not status:
        await pm.edit_text(
            "✦ ᴀssɪsᴛᴀɴᴛ ɪs ᴊᴏɪɴɪɴɢ ᴛʜᴇ ɢʀᴏᴜᴘ...",
            parse_mode=ParseMode.HTML,
        )
        ok = await try_join_assistant(chat_id, pm)
        if not ok:
            return

        await pm.edit_text(
            "✅ ᴀssɪsᴛᴀɴᴛ ʜᴀs ᴊᴏɪɴᴇᴅ ✓\n"
            "✦ ᴘʀᴏᴄᴇssɪɴɢ...",
            parse_mode=ParseMode.HTML,
        )

    try:
        result = await search_yt(query)
    except Exception as e:
        await pm.edit_text(
            f"⚡ sᴇᴀʀᴄʜ ғᴀɪʟᴇᴅ\n<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    if not result or not isinstance(result, tuple):
        await pm.edit_text("⚡ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ", parse_mode=ParseMode.HTML)
        return

    url, title, dur_iso, thumb = result

    secs = parse_dur(dur_iso)
    if secs > config.MAX_DURATION_SECONDS:
        await pm.edit_text(
            f"⚡ sᴏɴɢ ᴛᴏᴏ ʟᴏɴɢ\n"
            f"✦ ᴅᴜʀ : <code>{dur_iso}</code>\n"
            f"✦ ᴍᴀx : <code>{config.MAX_DURATION_SECONDS // 60} min</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    req = message.from_user.first_name if message.from_user else "Unknown"
    req_id = message.from_user.id if message.from_user else 0

    song = {
        "url": url,
        "title": title,
        "duration": dur_iso,
        "duration_seconds": secs,
        "requester": req,
        "requester_id": req_id,
        "thumbnail": thumb,
        "video": (cmd == "vplay"),
    }

    pos = add_to_queue(chat_id, song)

    if pos == 1:
        await play_song(chat_id, pm, song)
    else:
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏭️ sᴋɪᴩ", callback_data="skip"),
                InlineKeyboardButton("⏹️ ᴄʟᴇᴀʀ", callback_data="clear"),
            ]
        ])
        await message.reply(
            f"✅ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ\n"
            f"✦ ᴛɪᴛʟᴇ : <code>{short(title)}</code>\n"
            f"✦ ᴅᴜʀ : <code>{dur_iso}</code>\n"
            f"✦ ʀᴇϙᴜᴇsᴛᴇᴅ ʙʏ : <code>{req}</code>\n"
            f"✦ ᴩᴏs : <code>#{pos - 1}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        await pm.delete()
EOF
