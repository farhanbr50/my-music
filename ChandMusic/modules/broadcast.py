cat > ChandMusic/modules/broadcast.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import logging
import re

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    ChatAdminRequired,
    ChatForwardsRestricted,
    ChatWriteForbidden,
    FloodWait,
    MediaEmpty,
    MessageIdInvalid,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import Message

import config
from ChandMusic import bot
from ChandMusic.utils.db import get_broadcast_chats, get_broadcast_count, remove_broadcast_chat

logger = logging.getLogger(__name__)

_IS_BROADCASTING = False
_broadcast_lock = asyncio.Lock()


def _parse_flags(raw: str) -> tuple[bool, bool, bool, bool]:
    pin = bool(re.search(r"-pin(?!loud)", raw))
    pinloud = "-pinloud" in raw
    nogroup = "-nogroup" in raw
    user = "-user" in raw
    return pin, pinloud, nogroup, user


def _strip_flags(text: str) -> str:
    for flag in ("-pinloud", "-nogroup", "-user", "-pin"):
        text = text.replace(flag, "")
    return text.strip()


async def _send(target_id: int, bm: Message, broadcast_type: str, text: str) -> Message:
    if broadcast_type == "text":
        return await bot.send_message(target_id, text, parse_mode=ParseMode.HTML)

    try:
        return await bot.forward_messages(target_id, bm.chat.id, bm.id)
    except (ChatForwardsRestricted, MediaEmpty, MessageIdInvalid):
        return await bot.copy_message(target_id, bm.chat.id, bm.id)


@bot.on_message(filters.command(["broadcast", "gcast"]) & filters.user(config.OWNER_ID))
async def broadcast_cmd(_, message: Message) -> None:
    global _IS_BROADCASTING

    async with _broadcast_lock:
        if _IS_BROADCASTING:
            await message.reply(
                "⚡ A broadcast is already running.\n"
                "✦ Please wait for it to finish.",
                parse_mode=ParseMode.HTML,
            )
            return

        _IS_BROADCASTING = True
        try:
            await _run_broadcast(message)
        finally:
            _IS_BROADCASTING = False


async def _run_broadcast(message: Message) -> None:
    raw = message.text or ""
    try:
        raw_args = raw.split(None, 1)[1]
    except IndexError:
        raw_args = ""

    flag_pin, flag_pinloud, flag_nogroup, flag_user = _parse_flags(raw_args)
    clean_text = _strip_flags(raw_args)

    if message.reply_to_message:
        bm = message.reply_to_message
        broadcast_type = "reply"
    elif clean_text:
        bm = None
        broadcast_type = "text"
    else:
        await message.reply(
            "✦ Reply to a message or provide text.\n\n"
            "✦ Flags :\n"
            "<code>-pin</code>      → pin silently in groups\n"
            "<code>-pinloud</code>  → pin with notification\n"
            "<code>-nogroup</code>  → skip groups\n"
            "<code>-user</code>     → also send to private users",
            parse_mode=ParseMode.HTML,
        )
        return

    all_docs = get_broadcast_chats()
    counts = get_broadcast_count()
    groups = [d for d in all_docs if d.get("type") == "group"]
    private = [d for d in all_docs if d.get("type") == "private"]

    targets = (0 if flag_nogroup else len(groups)) + (len(private) if flag_user else 0)

    if targets == 0:
        await message.reply(
            "⚡ No targets found in broadcast list.",
            parse_mode=ParseMode.HTML,
        )
        return

    active_flags = " ".join(filter(None, [
        "-pin" if flag_pin else "",
        "-pinloud" if flag_pinloud else "",
        "-nogroup" if flag_nogroup else "",
        "-user" if flag_user else "",
    ])) or "none"

    pm = await message.reply(
        f"📢 Broadcast Started\n\n"
        f"✦ Total   : <code>{counts['total']}</code>\n"
        f"✦ Groups  : <code>{len(groups)}</code>\n"
        f"✦ Users   : <code>{len(private)}</code>\n"
        f"✦ Targets : <code>{targets}</code>\n"
        f"✦ Flags   : <code>{active_flags}</code>",
        parse_mode=ParseMode.HTML,
    )

    success_g = success_u = pinned = failed = 0

    if not flag_nogroup:
        for doc in groups:
            cid = int(doc["chat_id"])
            try:
                sent = await _send(cid, bm, broadcast_type, clean_text)
                success_g += 1

                if flag_pin or flag_pinloud:
                    try:
                        await bot.pin_chat_message(
                            cid,
                            sent.id,
                            disable_notification=not flag_pinloud,
                        )
                        pinned += 1
                    except ChatAdminRequired:
                        pass
                    except Exception:
                        pass

            except FloodWait as e:
                wait = int(e.value)
                if wait > 200:
                    failed += 1
                    continue
                await asyncio.sleep(wait)
                try:
                    await _send(cid, bm, broadcast_type, clean_text)
                    success_g += 1
                except Exception:
                    failed += 1

            except (UserIsBlocked, ChatWriteForbidden, PeerIdInvalid):
                remove_broadcast_chat(cid)
                failed += 1

            except Exception as e:
                logger.warning(f"⚡ [Broadcast] group {cid}: {e}")
                failed += 1

            await asyncio.sleep(0.4)

    if flag_user:
        for doc in private:
            uid = int(doc["chat_id"])
            try:
                await _send(uid, bm, broadcast_type, clean_text)
                success_u += 1

            except FloodWait as e:
                wait = int(e.value)
                if wait > 200:
                    failed += 1
                    continue
                await asyncio.sleep(wait)
                try:
                    await _send(uid, bm, broadcast_type, clean_text)
                    success_u += 1
                except Exception:
                    failed += 1

            except (UserIsBlocked, PeerIdInvalid):
                remove_broadcast_chat(uid)
                failed += 1

            except Exception as e:
                logger.warning(f"⚡ [Broadcast] user {uid}: {e}")
                failed += 1

            await asyncio.sleep(0.4)

    await pm.edit_text(
        "✅ Broadcast Completed ✅\n\n"
        f"✦ Groups : <code>{success_g}</code>\n"
        f"✦ Users  : <code>{success_u}</code>\n"
        f"✦ Pinned : <code>{pinned}</code>\n"
        f"✦ Failed : <code>{failed}</code>",
        parse_mode=ParseMode.HTML,
    )
EOF
