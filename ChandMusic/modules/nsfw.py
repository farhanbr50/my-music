cat > ChandMusic/modules/nsfw.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import json
import os

import aiohttp
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ChandMusic import bot, LOGGER
from ChandMusic.modules.block import user_allowed
from ChandMusic.utils.db import (
    is_nsfw_enabled,
    set_nsfw_enabled,
    approve_nsfw_user,
    disapprove_nsfw_user,
    is_nsfw_approved,
    get_nsfw_approved_users,
)
from ChandMusic.utils.permissions import is_user_authorized

DOWNLOAD_DIR = "downloads/nsfw"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

REPORT_AUTO_DELETE = 20


def _is_plain_text(_, __, message: Message) -> bool:
    return bool(message.text) and not message.text.startswith("/")


not_command = filters.create(_is_plain_text)
MEDIA_FILTER = (
    filters.photo
    | filters.video
    | filters.animation
    | filters.sticker
    | filters.document
)


async def _scan_file(path: str, content_type: str) -> dict | None:
    try:
        async with aiohttp.ClientSession() as session:
            with open(path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field(
                    "file", f,
                    filename=os.path.basename(path),
                    content_type=content_type,
                )
                data.add_field("thresholds", json.dumps(config.NSFW_THRESHOLDS))
                headers = {"x-api-key": config.NSFW_API_KEY}

                async with session.post(
                    f"{config.NSFW_API_URL}/detect/upload",
                    data=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        LOGGER.warning(f"⚡ [nsfw] API status {resp.status}")
                        return None
                    return await resp.json()
    except Exception as e:
        LOGGER.error(f"⚡ [nsfw] scan_file failed: {e}")
        return None


async def _scan_text(text: str) -> dict | None:
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"text": text, "x_api_key": config.NSFW_API_KEY}
            async with session.post(
                f"{config.NSFW_API_URL}/text/check",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
    except Exception as e:
        LOGGER.error(f"⚡ [nsfw] scan_text failed: {e}")
        return None


def _media_content_type(message: Message) -> str | None:
    if message.photo:
        return "image/jpeg"
    if message.video:
        return "video/mp4"
    if message.animation:
        return "video/mp4"
    if message.sticker:
        mime = message.sticker.mime_type or ""
        if "tgsticker" in mime:
            return "application/x-tgsticker"
        if "webm" in mime:
            return "video/webm"
        return "image/webp"
    if message.document:
        mime = message.document.mime_type or ""
        if mime.startswith("image/") or mime.startswith("video/") or "tgsticker" in mime:
            return mime
        return None
    return None


async def _auto_delete(message: Message, delay: int) -> None:
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


async def _extract_user(client, message: Message, args: list):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    if args:
        target = args[0]
        try:
            if target.lstrip("-").isdigit():
                return await client.get_users(int(target))
            return await client.get_users(target)
        except Exception:
            return None
    return None


def _build_report(result: dict) -> tuple[str, bool]:
    nsfw = result.get("nsfw", {}) or {}
    triggered = result.get("triggered")
    has_weapon = result.get("has_weapon", False)
    has_drugs = result.get("has_drugs", False)
    should_delete = result.get("should_delete", False)
    thresholds = result.get("thresholds_used", {}) or {}

    threshold_line = ""
    if triggered:
        category = triggered.capitalize()
        confidence = nsfw.get(triggered, 0) * 100
        thr = thresholds.get(triggered)
        if thr is not None:
            threshold_line = f"✦ Threshold: {thr * 100:.0f}%\n"
    elif has_weapon:
        category = "Weapon"
        confs = [d["confidence"] for d in result.get("detections", []) if d["type"] == "weapon"]
        confidence = (max(confs) * 100) if confs else 0
    elif has_drugs:
        category = "Drugs"
        confs = [d["confidence"] for d in result.get("detections", []) if d["type"] == "drug"]
        confidence = (max(confs) * 100) if confs else 0
    else:
        category = "Clean"
        confidence = nsfw.get("neutral", 0) * 100

    report = (
        f"🔞 NSFW Scan Report\n\n"
        f"📊 Category: <code>{category}</code>\n"
        f"📈 Confidence: <code>{confidence:.1f}%</code>\n"
        f"{threshold_line}"
    )

    if should_delete:
        report += "\n❌ This media has been deleted."

    return report, should_delete


@bot.on_message(filters.command("nsfw") & filters.group & user_allowed)
async def nsfw_toggle_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply(
            "⚡ Only admins can use this command.",
            parse_mode=ParseMode.HTML,
        )
        return

    chat_id = message.chat.id
    args = message.command[1:]

    if not args:
        state = is_nsfw_enabled(chat_id)
        await message.reply(
            f"✦ NSFW Filter: <code>{'✅ ON' if state else '❌ OFF'}</code>\n\n"
            "✦ Usage:\n"
            "<code>/nsfw on</code>  → Enable NSFW filter\n"
            "<code>/nsfw off</code> → Disable NSFW filter",
            parse_mode=ParseMode.HTML,
        )
        return

    cmd = args[0].lower()
    if cmd == "on":
        set_nsfw_enabled(chat_id, True)
        await message.reply(
            "✅ NSFW Filter Enabled\n"
            "✦ Inappropriate content will be automatically deleted.",
            parse_mode=ParseMode.HTML,
        )
    elif cmd == "off":
        set_nsfw_enabled(chat_id, False)
        await message.reply(
            "❌ NSFW Filter Disabled\n"
            "✦ No content will be scanned.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply(
            "⚡ Invalid option.\n"
            "✦ Usage: <code>/nsfw on</code> or <code>/nsfw off</code>",
            parse_mode=ParseMode.HTML,
        )


@bot.on_message(filters.command("nsfwapprove") & filters.group & user_allowed)
async def nsfw_approve_cmd(client, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply(
            "⚡ Only admins can use this command.",
            parse_mode=ParseMode.HTML,
        )
        return

    args = message.command[1:]

    if args and args[0].lower() == "list":
        users = get_nsfw_approved_users(message.chat.id)
        if not users:
            await message.reply(
                "⚡ No NSFW-approved users in this chat.",
                parse_mode=ParseMode.HTML,
            )
            return
        lines = "\n".join(f"• <code>{uid}</code>" for uid in users)
        await message.reply(
            f"✦ NSFW-Approved Users:\n{lines}",
            parse_mode=ParseMode.HTML,
        )
        return

    remove = bool(args) and args[-1].lower() in ("off", "remove", "-")
    target_args = args[:-1] if remove else args
    target = await _extract_user(client, message, target_args)

    if target is None:
        await message.reply(
            "✦ Reply to a user's message (or provide their ID/username)\n"
            "✦ Usage:\n"
            "• <code>/nsfwapprove</code> — reply to approve\n"
            "• <code>/nsfwapprove off</code> — reply to remove approval\n"
            "• <code>/nsfwapprove list</code> — view approved users",
            parse_mode=ParseMode.HTML,
        )
        return

    if remove:
        disapprove_nsfw_user(message.chat.id, target.id)
        await message.reply(
            f"✦ {target.mention} removed from the NSFW-approved list ❌",
            parse_mode=ParseMode.HTML,
        )
    else:
        approve_nsfw_user(message.chat.id, target.id)
        await message.reply(
            f"✦ {target.mention} NSFW-Approved ✅",
            parse_mode=ParseMode.HTML,
        )


@bot.on_message(MEDIA_FILTER & filters.group & user_allowed)
async def nsfw_media_scan(client, message: Message) -> None:
    if not is_nsfw_enabled(message.chat.id):
        return

    if message.from_user and is_nsfw_approved(message.chat.id, message.from_user.id):
        return

    content_type = _media_content_type(message)
    if content_type is None:
        return

    path = None
    try:
        path = await message.download(file_name=f"{DOWNLOAD_DIR}/")
    except Exception as e:
        LOGGER.error(f"⚡ [nsfw] download failed: {e}")
        return

    try:
        result = await _scan_file(path, content_type)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

    if not result:
        return

    report_text, should_delete = _build_report(result)

    if not should_delete:
        return

    try:
        await message.delete()
    except Exception as e:
        LOGGER.warning(f"⚡ [nsfw] could not delete message: {e}")

    user = message.from_user
    header = f"👤 User: {user.mention}\n\n" if user else ""

    sent = await client.send_message(
        message.chat.id,
        header + report_text,
        parse_mode=ParseMode.HTML,
    )
    asyncio.create_task(_auto_delete(sent, REPORT_AUTO_DELETE))


@bot.on_message(filters.text & filters.group & not_command & user_allowed)
async def nsfw_text_scan(client, message: Message) -> None:
    if not is_nsfw_enabled(message.chat.id):
        return

    if message.from_user and is_nsfw_approved(message.chat.id, message.from_user.id):
        return

    if len(message.text.strip()) < 2:
        return

    result = await _scan_text(message.text)

    if not result or not result.get("has_bad_words"):
        return

    try:
        await message.delete()
    except Exception as e:
        LOGGER.warning(f"⚡ [nsfw] could not delete text message: {e}")

    user = message.from_user
    mention = user.mention if user else "Someone"
    toxicity = result.get("toxicity_score", 0) * 100

    warn_text = (
        "🚫 Message Deleted\n\n"
        f"👤 User: {mention}\n"
        f"⚠️ Reason: Bad word(s) detected\n"
        f"📈 Toxicity: {toxicity:.0f}%"
    )

    sent = await client.send_message(
        message.chat.id,
        warn_text,
        parse_mode=ParseMode.HTML,
    )
    asyncio.create_task(_auto_delete(sent, REPORT_AUTO_DELETE))
EOF
