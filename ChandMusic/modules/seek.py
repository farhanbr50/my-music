cat > ChandMusic/modules/seek.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import time

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from ChandMusic import bot, call_py, LOGGER
from ChandMusic.core.queue import peek_current
from ChandMusic.modules.block import group_allowed, user_allowed
from ChandMusic.utils.formatters import fmt_time, parse_dur, progress_bar, short
from ChandMusic.utils.youtube import resolve_stream

_seek_state: dict[int, dict] = {}


def set_seek_state(chat_id: int, offset: int) -> None:
    _seek_state[chat_id] = {"start_ts": time.time(), "offset": offset}


def get_current_position(chat_id: int) -> int:
    state = _seek_state.get(chat_id)
    if not state:
        return 0
    return state["offset"] + int(time.time() - state["start_ts"])


def clear_seek_state(chat_id: int) -> None:
    _seek_state.pop(chat_id, None)


async def _seek_to(chat_id: int, target_sec: int, message: Message) -> None:
    from pytgcalls.types import AudioQuality, MediaStream

    song = peek_current(chat_id)
    if not song:
        await message.reply("⚡ Nothing is playing right now.", parse_mode=ParseMode.HTML)
        return

    total_sec = parse_dur(song.get("duration", "0:00"))
    target_sec = max(0, min(target_sec, total_sec - 1))

    pm = await message.reply(
        f"⏩ Seeking to <code>{fmt_time(target_sec)}</code>...",
        parse_mode=ParseMode.HTML,
    )

    try:
        media_path = await resolve_stream(song["url"])
    except Exception as e:
        await pm.edit_text(
            f"⚡ Seek failed — could not resolve stream.\n<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await call_py.change_stream(
            chat_id,
            MediaStream(
                media_path,
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters=f"-ss {target_sec}",
            ),
        )
    except Exception as e:
        try:
            await call_py.play(
                chat_id,
                MediaStream(
                    media_path,
                    audio_parameters=AudioQuality.HIGH,
                    video_flags=MediaStream.Flags.IGNORE,
                    ffmpeg_parameters=f"-ss {target_sec}",
                ),
            )
        except Exception as e2:
            await pm.edit_text(
                f"⚡ Seek failed.\n<code>{e2}</code>",
                parse_mode=ParseMode.HTML,
            )
            return

    set_seek_state(chat_id, target_sec)

    caption = (
        "╔══════════════════════════════════════════╗\n"
        "║    🎵 ɴᴏᴡ ᴘʟᴀʏɪɴɢ 🎵               ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        f"✦ ᴛɪᴛʟᴇ : {short(song['title'])}\n"
        f"✦ ᴅᴜʀᴀᴛɪᴏɴ : {song.get('duration', '?')}\n"
        f"✦ ʀᴇϙᴜᴇsᴛᴇᴅ ʙʏ : {song['requester']}\n"
        f"✦ sᴇᴇᴋᴇᴅ ᴛᴏ : <code>{fmt_time(target_sec)}</code>\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    )

    btns = [
        InlineKeyboardButton("▶️", callback_data="resume"),
        InlineKeyboardButton("⏸️", callback_data="pause"),
        InlineKeyboardButton("⏭️", callback_data="skip"),
        InlineKeyboardButton("⏹️", callback_data="stop"),
    ]
    kb = InlineKeyboardMarkup([btns])

    try:
        await pm.delete()
    except Exception:
        pass

    await message.reply_photo(
        photo=song.get("thumbnail", "https://telegra.ph/file/1a3c152717eb9d2e94dc2.mp4"),
        caption=caption,
        reply_markup=kb,
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(
    filters.group
    & filters.regex(r"^/seek(?:@\w+)?\s+(?P<sec>\d+)$")
    & group_allowed
    & user_allowed
)
async def seek_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    try:
        sec = int(message.matches[0].group("sec"))
    except Exception:
        await message.reply(
            "✦ Usage: <code>/seek 30</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    song = peek_current(chat_id)
    if not song:
        await message.reply("⚡ Nothing is playing right now.", parse_mode=ParseMode.HTML)
        return

    current_pos = get_current_position(chat_id)
    target = current_pos + sec
    await _seek_to(chat_id, target, message)


@bot.on_message(
    filters.group
    & filters.regex(r"^/seekback(?:@\w+)?\s+(?P<sec>\d+)$")
    & group_allowed
    & user_allowed
)
async def seekback_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    try:
        sec = int(message.matches[0].group("sec"))
    except Exception:
        await message.reply(
            "✦ Usage: <code>/seekback 30</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    song = peek_current(chat_id)
    if not song:
        await message.reply("⚡ Nothing is playing right now.", parse_mode=ParseMode.HTML)
        return

    current_pos = get_current_position(chat_id)
    target = max(0, current_pos - sec)
    await _seek_to(chat_id, target, message)
EOF
