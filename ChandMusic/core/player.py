cat > ChandMusic/core/player.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import math
import random
import time

from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls.exceptions import NoActiveGroupCall
from ntgcalls import TelegramServerError

import config
from ChandMusic import LOGGER, bot, call_py
from ChandMusic.core.autoplay import _autoplay_fetching, is_autoplay, maybe_refetch
from ChandMusic.core.queue import clear_queue, peek_current, pop_current, remove_from_queue
from ChandMusic.utils.formatters import fmt_time, parse_dur, progress_bar, short
from ChandMusic.utils.helpers import delete_file
from ChandMusic.utils.youtube import resolve_stream


async def _ensure_vc(chat_id: int) -> bool:
    try:
        chat_id = int(chat_id)
        chat = await call_py._app.get_chat(chat_id)
        await call_py._app.invoke(
            CreateGroupCall(
                peer=await call_py._app.resolve_peer(chat.id),
                random_id=random.randint(10000, 99999),
            )
        )
        LOGGER.info(f"✨ [VC] Created in {chat_id}")
        await asyncio.sleep(2)
        return True

    except TelegramServerError as e:
        LOGGER.error(f"⚡ [VC] TelegramServerError: {e}")
        await bot.send_message(
            chat_id,
            "⚡ ᴠᴄ ꜱᴛᴀʀᴛ ғᴀɪʟᴇᴅ (Telegram Server)\n"
            f"<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return False

    except Exception as e:
        err = str(e).lower()
        if "already" in err or "groupcall_already_started" in err:
            return True

        if "chat_admin_required" in err or "admin" in err:
            await bot.send_message(
                chat_id,
                "⚡ ᴠᴄ ꜱᴛᴀʀᴛ ᴘᴇʀᴍɪssɪᴏɴ ᴍɪssɪɴɢ\n\n"
                "⭐ ɢɪᴠᴇ ᴀssɪsᴛᴀɴᴛ :\n"
                "• <code>Manage Video Chats</code>\n"
                "• <code>Admin Rights</code>",
                parse_mode=ParseMode.HTML,
            )
            return False

        LOGGER.error(f"⚡ [VC ERROR] {e}")
        await bot.send_message(
            chat_id,
            "⚡ ᴠᴄ ꜱᴛᴀʀᴛ ғᴀɪʟᴇᴅ\n"
            f"<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return False


async def play_song(chat_id: int, message, song: dict) -> None:
    chat_id = int(chat_id)
    url = song.get("url")

    if not url:
        return

    loading_text = (
        f"🎵 ʟᴏᴀᴅɪɴɢ : {short(song['title'])}"
    )

    try:
        await message.edit(loading_text, parse_mode=ParseMode.HTML)
    except Exception:
        message = await bot.send_message(
            chat_id,
            loading_text,
            parse_mode=ParseMode.HTML,
        )

    try:
        media_path = await resolve_stream(url)
    except Exception as e:
        try:
            remove_from_queue(chat_id, 0)
        except Exception:
            pass

        await bot.send_message(
            chat_id,
            f"⚡ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ\n\n<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    is_video = song.get("video", False)

    if not is_video:
        try:
            from ChandMusic.modules.effects import maybe_apply_effects
            media_path = await maybe_apply_effects(chat_id, media_path)
        except Exception as fx_err:
            LOGGER.warning(f"⭐ [Effects] Skipped: {fx_err}")

    played = False

    for attempt in range(2):
        try:
            if is_video:
                await call_py.play(
                    chat_id,
                    MediaStream(
                        media_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.HD_720p,
                    ),
                )
            else:
                await call_py.play(
                    chat_id,
                    MediaStream(
                        media_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.Flags.IGNORE,
                    ),
                )

            played = True
            break

        except NoActiveGroupCall:
            if attempt == 0:
                LOGGER.info(f"✨ [VC] NoActiveGroupCall — Creating VC in {chat_id}")
                ok = await _ensure_vc(chat_id)
                if ok:
                    continue
                try:
                    remove_from_queue(chat_id, 0)
                except Exception:
                    pass
                return

        except TelegramServerError as e:
            LOGGER.error(f"⚡ [PLAY] TelegramServerError: {e}")
            try:
                remove_from_queue(chat_id, 0)
            except Exception:
                pass
            await bot.send_message(
                chat_id,
                "⚡ ᴘʟᴀʏʙᴀᴄᴋ ғᴀɪʟᴇᴅ (Telegram Server)\n"
                f"<code>{e}</code>",
                parse_mode=ParseMode.HTML,
            )
            return

        except Exception as e:
            err = str(e).lower()

            vc_missing = any(
                x in err
                for x in (
                    "groupcallnotfound",
                    "not_in_group_call",
                    "groupcall_forbidden",
                    "not in group call",
                    "no active group call",
                )
            )

            if vc_missing and attempt == 0:
                LOGGER.info(f"✨ [VC] Creating VC in {chat_id}")
                ok = await _ensure_vc(chat_id)
                if ok:
                    continue
                try:
                    remove_from_queue(chat_id, 0)
                except Exception:
                    pass
                return

            if "chat_admin_required" in err or "admin" in err:
                try:
                    remove_from_queue(chat_id, 0)
                except Exception:
                    pass
                await bot.send_message(
                    chat_id,
                    "⚡ ᴠᴄ ꜱᴛᴀʀᴛ ᴘᴇʀᴍɪssɪᴏɴ ᴍɪssɪɴɢ\n\n"
                    "⭐ ᴘʟᴇᴀsᴇ ɢɪᴠᴇ :\n"
                    "• <code>Manage Video Chats</code>\n"
                    "• <code>Admin Rights</code>\n\n"
                    "⚡ ᴀssɪsᴛᴀɴᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ",
                    parse_mode=ParseMode.HTML,
                )
                LOGGER.error(f"⚡ [ADMIN ERROR] {e}")
                return

            try:
                remove_from_queue(chat_id, 0)
            except Exception:
                pass

            await bot.send_message(
                chat_id,
                "⚡ ᴘʟᴀʏʙᴀᴄᴋ ғᴀɪʟᴇᴅ\n\n"
                f"<code>{e}</code>",
                parse_mode=ParseMode.HTML,
            )
            LOGGER.error(f"⚡ [PLAY ERROR] {e}")
            return

    if not played:
        return

    try:
        from ChandMusic.modules.seek import set_seek_state
        set_seek_state(chat_id, 0)
    except Exception:
        pass

    try:
        from ChandMusic.database import (
            add_served_chat,
            add_served_user,
            increment_play_count,
        )

        add_served_chat(chat_id)
        requester_id = song.get("requester_id")
        if requester_id:
            add_served_user(requester_id)
        increment_play_count(chat_id)
    except Exception as db_err:
        LOGGER.warning(f"⭐ [DB ERROR] {db_err}")

    total = parse_dur(song.get("duration", "0:00"))

    caption = (
        "╔══════════════════════════════════════════╗\n"
        "║    🎵 ɴᴏᴡ ᴘʟᴀʏɪɴɢ 🎵               ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        f"✦ ᴛɪᴛʟᴇ : {short(song['title'])}\n"
        f"✦ ᴅᴜʀᴀᴛɪᴏɴ : {song.get('duration', '?')}\n"
        f"✦ ʀᴇϙᴜᴇsᴛᴇᴅ ʙʏ : {song['requester']}\n\n"
        "◈ ── ── ── ── ── ── ── ◈\n"
        "  ⚡ ғᴀsᴛ • sᴍᴏᴏᴛʜ • ᴘᴏᴡᴇʀꜰᴜʟ\n"
        "◈ ── ── ── ── ── ── ── ◈\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    )

    btns = [
        InlineKeyboardButton("⏮️", callback_data="back"),
        InlineKeyboardButton("⏪", callback_data="seekback"),
        InlineKeyboardButton("⏸️", callback_data="pause"),
        InlineKeyboardButton("⏩", callback_data="seek"),
        InlineKeyboardButton("⏭️", callback_data="skip"),
    ]

    bar = progress_bar(0, total)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(bar, callback_data="noop")],
        btns,
        [
            InlineKeyboardButton("⏹️ sᴛᴏᴘ", callback_data="stop"),
            InlineKeyboardButton("🔁 ʟᴏᴏᴘ", callback_data="loop"),
            InlineKeyboardButton("🎵 ᴇғғᴇᴄᴛs", callback_data="effects_menu"),
        ],
        [
            InlineKeyboardButton("✨ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ", url=config.BOT_LINK),
        ],
    ])

    thumb = song.get("thumbnail")

    try:
        pmsg = await message.reply_photo(
            photo=thumb,
            caption=caption,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pmsg = await bot.send_message(
            chat_id,
            caption,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )

    try:
        await message.delete()
    except Exception:
        pass

    asyncio.create_task(
        _update_progress(
            chat_id,
            pmsg,
            time.time(),
            total,
            caption,
        )
    )

    if config.LOGGER_ID:
        asyncio.create_task(
            bot.send_message(
                config.LOGGER_ID,
                "✨ #ɴᴏᴡᴘʟᴀʏɪɴɢ ✨\n"
                f"• 🎵 ᴛɪᴛʟᴇ : {song.get('title')}\n"
                f"• ⏱️ ᴅᴜʀ : {song.get('duration')}\n"
                f"• 👤 ʀᴇϙᴜᴇsᴛᴇᴅ ʙʏ : {song.get('requester')}",
                parse_mode=ParseMode.HTML,
            )
        )


async def _update_progress(chat_id: int, msg, start: float, total: float, base_caption: str) -> None:
    while True:
        elapsed = time.time() - start
        if elapsed >= total:
            break

        current = peek_current(chat_id)
        if not current:
            break

        bar = progress_bar(elapsed, total)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(bar, callback_data="noop")],
            [
                InlineKeyboardButton("⏮️", callback_data="back"),
                InlineKeyboardButton("⏪", callback_data="seekback"),
                InlineKeyboardButton("⏸️", callback_data="pause"),
                InlineKeyboardButton("⏩", callback_data="seek"),
                InlineKeyboardButton("⏭️", callback_data="skip"),
            ],
            [
                InlineKeyboardButton("⏹️ sᴛᴏᴘ", callback_data="stop"),
                InlineKeyboardButton("🔁 ʟᴏᴏᴘ", callback_data="loop"),
                InlineKeyboardButton("🎵 ᴇғғᴇᴄᴛs", callback_data="effects_menu"),
            ],
            [
                InlineKeyboardButton("✨ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ", url=config.BOT_LINK),
            ],
        ])

        try:
            await msg.edit_caption(
                caption=base_caption + f"\n\n<code>{bar}</code>",
                reply_markup=kb,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass

        await asyncio.sleep(5)
EOF
