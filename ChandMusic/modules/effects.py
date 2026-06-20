cat > ChandMusic/modules/effects.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import os

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ChandMusic import LOGGER, bot, call_py
from ChandMusic.core.queue import peek_current
from ChandMusic.modules.block import group_allowed, user_allowed
from ChandMusic.utils.formatters import short
from ChandMusic.utils.youtube import resolve_stream

_cache: dict[int, dict] = {}
SPEED_DEFAULT = 1.0
BASS_DEFAULT = 0


def _db_save(chat_id: int) -> None:
    try:
        from ChandMusic.utils.db import save_chat_effects
        s = _get(chat_id)
        save_chat_effects(chat_id, s["speed"], s["bass"], s["enabled"])
    except Exception as e:
        LOGGER.warning(f"⭐ [Effects] DB save failed: {e}")


def _db_load(chat_id: int) -> dict:
    try:
        from ChandMusic.utils.db import load_chat_effects
        return load_chat_effects(chat_id)
    except Exception:
        return {"speed": 1.0, "bass": 0, "enabled": False}


def _get(chat_id: int) -> dict:
    if chat_id not in _cache:
        _cache[chat_id] = _db_load(chat_id)
    return _cache[chat_id]


def get_effects(chat_id: int) -> dict:
    return _get(chat_id).copy()


def set_speed(chat_id: int, speed: float) -> None:
    _get(chat_id)["speed"] = speed
    _db_save(chat_id)


def set_bass(chat_id: int, bass: int) -> None:
    _get(chat_id)["bass"] = bass
    _db_save(chat_id)


def set_enabled(chat_id: int, val: bool) -> None:
    _get(chat_id)["enabled"] = val
    _db_save(chat_id)


def is_effects_on(chat_id: int) -> bool:
    return _get(chat_id).get("enabled", False)


def clear_effects(chat_id: int) -> None:
    _cache.pop(chat_id, None)
    try:
        from ChandMusic.utils.db import delete_chat_effects
        delete_chat_effects(chat_id)
    except Exception:
        pass


def _build_af(speed: float, bass: int) -> str | None:
    parts = []
    if bass and bass > 0:
        parts.append(f"equalizer=f=80:t=h:width=200:g={min(bass, 20)}")
    if speed and speed != 1.0:
        speed = round(max(0.25, min(speed, 4.0)), 2)
        if 0.5 <= speed <= 2.0:
            parts.append(f"atempo={speed}")
        elif speed < 0.5:
            parts.append("atempo=0.5,atempo=0.5")
        else:
            chain = []
            rem = speed
            while rem > 2.0:
                chain.append("atempo=2.0")
                rem /= 2.0
            chain.append(f"atempo={round(rem, 2)}")
            parts.append(",".join(chain))
    return ",".join(parts) if parts else None


async def _process_file(src: str, speed: float, bass: int) -> str:
    af = _build_af(speed, bass)
    if not af:
        return src

    os.makedirs("downloads/effects", exist_ok=True)
    base = os.path.splitext(os.path.basename(src))[0]
    tag = f"s{str(speed).replace('.', '')}_b{bass}"
    out = f"downloads/effects/{base}_{tag}.mp3"

    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out

    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-af", af,
        "-vn", "-acodec", "libmp3lame", "-b:a", "192k",
        out,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await asyncio.wait_for(proc.communicate(), timeout=120)

    if proc.returncode != 0 or not os.path.exists(out):
        raise Exception("ffmpeg processing failed")

    return out


async def _stream_from(chat_id: int, file_path: str, seek_sec: int = 0) -> None:
    from pytgcalls.types import AudioQuality, MediaStream

    ms_kwargs = dict(
        audio_parameters=AudioQuality.HIGH,
        video_flags=MediaStream.Flags.IGNORE,
    )
    if seek_sec > 0:
        ms_kwargs["ffmpeg_parameters"] = f"-ss {seek_sec}"

    try:
        await call_py.change_stream(chat_id, MediaStream(file_path, **ms_kwargs))
    except Exception:
        await call_py.play(chat_id, MediaStream(file_path, **ms_kwargs))


async def apply_effects_now(chat_id: int, message: Message, *, seek_sec: int = -1) -> None:
    from ChandMusic.utils.youtube import resolve_stream
    from ChandMusic.modules.seek import get_current_position, set_seek_state

    song = peek_current(chat_id)
    if not song:
        await message.reply("⚡ No song is currently playing.", parse_mode=ParseMode.HTML)
        return

    state = _get(chat_id)
    speed = state["speed"]
    bass = state["bass"]

    pm = await message.reply("✦ Applying effects, please wait...", parse_mode=ParseMode.HTML)

    try:
        src = await resolve_stream(song["url"])
    except Exception as e:
        await pm.edit_text(f"⚡ Stream resolve failed.\n<code>{e}</code>", parse_mode=ParseMode.HTML)
        return

    try:
        processed = await _process_file(src, speed, bass)
    except Exception as e:
        await pm.edit_text(f"⚡ ffmpeg error: <code>{e}</code>", parse_mode=ParseMode.HTML)
        return

    pos = get_current_position(chat_id) if seek_sec == -1 else seek_sec
    try:
        await _stream_from(chat_id, processed, seek_sec=pos)
    except Exception as e:
        await pm.edit_text(f"⚡ Playback failed: <code>{e}</code>", parse_mode=ParseMode.HTML)
        return

    set_seek_state(chat_id, pos)

    speed_label = f"{speed}x" if speed != 1.0 else "Normal (1.0x)"
    bass_label = f"{bass} dB boost" if bass > 0 else "Off"
    pos_label = f"{pos // 60}:{pos % 60:02d}"

    await pm.edit_text(
        f"✅ Effects Applied ✓\n\n"
        f"✦ Song     : {short(song['title'])}\n"
        f"✦ Position : <code>{pos_label}</code>\n"
        f"✦ Speed    : <code>{speed_label}</code>\n"
        f"✦ Bass     : <code>{bass_label}</code>",
        parse_mode=ParseMode.HTML,
    )


async def maybe_apply_effects(chat_id: int, file_path: str) -> str:
    state = _get(chat_id)
    if not state.get("enabled", False):
        return file_path
    speed = state["speed"]
    bass = state["bass"]
    if speed == 1.0 and bass == 0:
        return file_path
    try:
        return await _process_file(file_path, speed, bass)
    except Exception as e:
        LOGGER.warning(f"⭐ [Effects] Auto-apply failed for {chat_id}: {e}")
        return file_path


@bot.on_message(
    filters.group
    & filters.regex(r"^/speed(?:@\w+)?\s+(?P<val>[\d.]+)$")
    & group_allowed
    & user_allowed
)
async def speed_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    try:
        val = round(float(message.matches[0].group("val")), 2)
    except ValueError:
        await message.reply(
            "⚡ Invalid value.\n✦ Usage : <code>/speed 1.5</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    if not (0.25 <= val <= 4.0):
        await message.reply(
            "⚡ Speed must be between <code>0.25</code> and <code>4.0</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    set_speed(chat_id, val)
    try:
        await message.delete()
    except Exception:
        pass
    await apply_effects_now(chat_id, message)


@bot.on_message(
    filters.group
    & filters.regex(r"^/speedreset(?:@\w+)?$")
    & group_allowed
    & user_allowed
)
async def speedreset_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    set_speed(chat_id, SPEED_DEFAULT)
    try:
        await message.delete()
    except Exception:
        pass
    await apply_effects_now(chat_id, message)


@bot.on_message(
    filters.group
    & filters.regex(r"^/bass(?:@\w+)?\s+(?P<val>\d+)$")
    & group_allowed
    & user_allowed
)
async def bass_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    try:
        val = int(message.matches[0].group("val"))
    except ValueError:
        await message.reply(
            "⚡ Invalid value.\n✦ Usage : <code>/bass 10</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    if not (1 <= val <= 20):
        await message.reply(
            "⚡ Bass must be between <code>1</code> and <code>20</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    set_bass(chat_id, val)
    try:
        await message.delete()
    except Exception:
        pass
    await apply_effects_now(chat_id, message)


@bot.on_message(
    filters.group
    & filters.regex(r"^/bassoff(?:@\w+)?$")
    & group_allowed
    & user_allowed
)
async def bassoff_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    set_bass(chat_id, BASS_DEFAULT)
    try:
        await message.delete()
    except Exception:
        pass
    await apply_effects_now(chat_id, message)


@bot.on_message(
    filters.group
    & filters.regex(r"^/effecton(?:@\w+)?$")
    & group_allowed
    & user_allowed
)
async def effecton_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    set_enabled(chat_id, True)
    state = _get(chat_id)
    speed_label = f"{state['speed']}x" if state['speed'] != 1.0 else "Normal (1.0x)"
    bass_label = f"{state['bass']} dB" if state['bass'] > 0 else "Off"
    await message.reply(
        "✅ Effects Enabled ✓\n\n"
        "✦ All songs in this group will now play with effects.\n\n"
        f"✦ Speed  : <code>{speed_label}</code>\n"
        f"✦ Bass   : <code>{bass_label}</code>\n\n"
        "💡 Use /effectoff to disable. Settings are saved across restarts.",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(
    filters.group
    & filters.regex(r"^/effectoff(?:@\w+)?$")
    & group_allowed
    & user_allowed
)
async def effectoff_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    set_enabled(chat_id, False)
    await message.reply(
        "❌ Effects Disabled ❌\n\n"
        "✦ Songs will now play without any effects.",
        parse_mode=ParseMode.HTML,
    )
EOF
