cat > ChandMusic/modules/callbacks.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio

from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from ChandMusic import bot, call_py
from ChandMusic.core.call import leave_vc
from ChandMusic.core.player import play_song
from ChandMusic.core.queue import clear_queue, peek_current, pop_current, queue_size
from ChandMusic.utils.db import is_user_blocked_db
from ChandMusic.utils.formatters import short
from ChandMusic.utils.helpers import delete_file
from ChandMusic.utils.permissions import is_user_authorized


_HELP_KB = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("ᴧᴅᴍɪɴ", callback_data="help_admin"),
        InlineKeyboardButton("ᴧ-ᴘʟᴀʏ", callback_data="help_autoplay"),
        InlineKeyboardButton("ɢ-ᴄᴧsᴛ", callback_data="help_gcast"),
    ],
    [
        InlineKeyboardButton("ʙʟ-ᴄʜᴧᴛ", callback_data="help_blchat"),
        InlineKeyboardButton("ʙʟ-ᴜsᴇʀs", callback_data="help_blusers"),
        InlineKeyboardButton("ᴘɪɴɢ", callback_data="help_ping"),
    ],
    [
        InlineKeyboardButton("ᴘʟᴀʏ", callback_data="help_play"),
        InlineKeyboardButton("sᴘᴇᴇᴅ", callback_data="help_speed"),
        InlineKeyboardButton("ɪɴғᴏ", callback_data="help_info"),
    ],
    [
        InlineKeyboardButton("⌯ ʜᴏᴍᴇ ⌯", callback_data="go_back"),
    ],
])

_BACK_KB = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⌯ ʙᴀᴄᴋ ⌯", callback_data="show_help"),
    ]
])


_HELP_TEXTS = {

    "help_admin": (
        "╔══════════════════════════════════════════╗\n"
        "║    ⚙️ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs                 ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /pause\n"
        "  → ᴘᴀᴜsᴇ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀʏʙᴀᴄᴋ\n\n"
        "✦ /resume\n"
        "  → ʀᴇsᴜᴍᴇ ᴘᴀᴜsᴇᴅ ᴘʟᴀʏʙᴀᴄᴋ\n\n"
        "✦ /skip\n"
        "  → sᴋɪᴩ ᴛᴏ ɴᴇxᴛ sᴏɴɢ\n\n"
        "✦ /stop or /end\n"
        "  → sᴛᴏᴩ ᴘʟᴀʏʙᴀᴄᴋ & ʟᴇᴀᴠᴇ ᴠᴄ\n\n"
        "✦ /clear\n"
        "  → ᴄʟᴇᴀʀ ᴀʟʟ sᴏɴɢs ɪɴ ǫᴜᴇᴜᴇ\n\n"
        "✦ /seek <seconds>\n"
        "  → sᴇᴇᴋ ғᴏʀᴡᴀʀᴅ ʙʏ ɴ sᴇᴄᴏɴᴅs\n\n"
        "✦ /seekback <seconds>\n"
        "  → sᴇᴇᴋ ʙᴀᴄᴋᴡᴀʀᴅ ʙʏ ɴ sᴇᴄᴏɴᴅs\n\n"
        "✦ /reboot\n"
        "  → ʀᴇsᴇᴛ ᴄʜᴀᴛ sᴛᴀᴛᴇ & ʟᴇᴀᴠᴇ ᴠᴄ\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),

    "help_autoplay": (
        "╔══════════════════════════════════════════╗\n"
        "║    🔁 ᴀᴜᴛᴏᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs              ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /autoplay <query>\n"
        "  → ᴄᴏɴᴛɪɴᴜᴏᴜsʟʏ ᴘʟᴀʏ sᴏɴɢs\n"
        "  → ʙᴀsᴇᴅ ᴏɴ ʏᴏᴜʀ ǫᴜᴇʀʏ\n\n"
        "✦ /end or /stop\n"
        "  → sᴛᴏᴩ ᴀᴜᴛᴏᴩʟᴀʏ & ᴄʟᴇᴀʀ ǫᴜᴇᴜᴇ\n\n"
        "💡 ᴇxᴀᴍᴩʟᴇ :\n"
        "  <code>/autoplay sidhu moose wala</code>\n"
        "  <code>/autoplay arijit singh</code>\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),

    "help_gcast": (
        "╔══════════════════════════════════════════╗\n"
        "║    📢 ɢ-ᴄᴀsᴛ ᴄᴏᴍᴍᴀɴᴅs                ║\n"
        "║    (ᴏᴡɴᴇʀ ᴏɴʟʏ)                       ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /broadcast or /gcast\n"
        "  → ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴍsɢ ᴏʀ ᴛʏᴩᴇ ᴛᴇxᴛ\n\n"
        "✦ ғʟᴀɢs :\n"
        "  <code>-pin</code>      → ᴩɪɴ sɪʟᴇɴᴛʟʏ ɪɴ ɢʀᴏᴜᴩs\n"
        "  <code>-pinloud</code>  → ᴩɪɴ ᴡɪᴛʜ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ\n"
        "  <code>-nogroup</code>  → sᴋɪᴩ ɢʀᴏᴜᴩs\n"
        "  <code>-user</code>     → ᴀʟsᴏ sᴇɴᴅ ᴛᴏ ᴜsᴇʀs\n\n"
        "💡 ᴇxᴀᴍᴩʟᴇ :\n"
        "  <code>/gcast -pin</code>           <i>(reply)</i>\n"
        "  <code>/gcast -user Hello!</code>   <i>(text)</i>\n"
        "  <code>/gcast -nogroup -user</code> <i>(reply, users only)</i>\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),

    "help_blchat": (
        "╔══════════════════════════════════════════╗\n"
        "║    🚫 ʙʟᴏᴄᴋ ᴄʜᴀᴛ ᴄᴏᴍᴍᴀɴᴅs            ║\n"
        "║    (ᴏᴡɴᴇʀ ᴏɴʟʏ)                       ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /gblock\n"
        "  → ʙʟᴏᴄᴋ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴩ\n"
        "  → ɴᴏ ᴄᴏᴍᴍᴀɴᴅs ᴡɪʟʟ ᴡᴏʀᴋ\n\n"
        "✦ /gblock -100xxxxxxx\n"
        "  → ʙʟᴏᴄᴋ ʙʏ ᴄʜᴀᴛ ɪᴅ\n\n"
        "✦ /gunblock\n"
        "  → ᴜɴʙʟᴏᴄᴋ ɢʀᴏᴜᴩ\n\n"
        "✦ /gunblock -100xxxxxxx\n"
        "  → ᴜɴʙʟᴏᴄᴋ ʙʏ ᴄʜᴀᴛ ɪᴅ\n\n"
        "✦ /blocklist\n"
        "  → ʟɪsᴛ ᴀʟʟ ʙʟᴏᴄᴋᴇᴅ ᴄʜᴀᴛs\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),

    "help_blusers": (
        "╔══════════════════════════════════════════╗\n"
        "║    🚫 ʙʟᴏᴄᴋ ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs            ║\n"
        "║    (ᴏᴡɴᴇʀ ᴏɴʟʏ)                       ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /ublock <user_id>\n"
        "  → ʙʟᴏᴄᴋ ᴀ ᴜsᴇʀ\n\n"
        "✦ /ublock reply\n"
        "  → ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍsɢ ᴛᴏ ʙʟᴏᴄᴋ\n\n"
        "✦ /unblock <user_id>\n"
        "  → ᴜɴʙʟᴏᴄᴋ ᴀ ᴜsᴇʀ\n\n"
        "✦ /unblock reply\n"
        "  → ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍsɢ ᴛᴏ ᴜɴʙʟᴏᴄᴋ\n\n"
        "✦ /userlist\n"
        "  → ʟɪsᴛ ᴀʟʟ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),

    "help_ping": (
        "╔══════════════════════════════════════════╗\n"
        "║    🏓 ᴘɪɴɢ ᴄᴏᴍᴍᴀɴᴅ                   ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /ping\n"
        "  → ᴄʜᴇᴄᴋ ʙᴏᴛ's ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ\n"
        "  → sʏsᴛᴇᴍ sᴛᴀᴛs (RAM, CPU, Disk)\n"
        "  → ᴘʏᴛɢᴄ ʟᴀᴛᴇɴᴄʏ\n\n"
        "💡 sʜᴏᴡs :\n"
        "  • ʙᴏᴛ ʟᴀᴛᴇɴᴄʏ\n"
        "  • ᴜᴘᴛɪᴍᴇ\n"
        "  • RAM ᴜsᴀɢᴇ\n"
        "  • CPU ᴜsᴀɢᴇ\n"
        "  • ᴅɪsᴋ sᴘᴀᴄᴇ\n"
        "  • ᴘʏᴛɢᴄ ʟᴀᴛᴇɴᴄʏ\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),

    "help_play": (
        "╔══════════════════════════════════════════╗\n"
        "║    🎵 ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs                   ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /play <song name>\n"
        "  → ᴘʟᴀʏ ᴀᴜᴅɪᴏ ғʀᴏᴍ YouTube\n\n"
        "✦ /vplay <song name>\n"
        "  → ᴘʟᴀʏ ᴠɪᴅᴇᴏ ғʀᴏᴍ YouTube\n\n"
        "✦ /play YouTube URL\n"
        "  → ᴘʟᴀʏ ғʀᴏᴍ ʟɪɴᴋ\n\n"
        "✦ /play reply to audio\n"
        "  → ᴘʟᴀʏ ᴀɴ ᴀᴜᴅɪᴏ ғɪʟᴇ\n\n"
        "✦ /play reply to video\n"
        "  → ᴘʟᴀʏ ᴀ ᴠɪᴅᴇᴏ ғɪʟᴇ\n\n"
        "💡 ᴛɪᴘ :\n"
        "  → ᴜsᴇ <code>/play bollywood songs</code>\n"
        "  → ᴜsᴇ <code>/vplay music video</code>\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),

    "help_speed": (
        "╔══════════════════════════════════════════╗\n"
        "║    ⚡ sᴘᴇᴇᴅ & ʙᴀss ᴄᴏᴍᴍᴀɴᴅs          ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /speed <value>\n"
        "  → ᴄʜᴀɴɢᴇ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ\n"
        "  → ʀᴀɴɢᴇ : 0.25 ᴛᴏ 4.0\n\n"
        "✦ /speedreset\n"
        "  → ʀᴇsᴇᴛ sᴘᴇᴇᴅ ᴛᴏ 1.0x\n\n"
        "✦ /bass <value>\n"
        "  → ᴀᴅᴅ ʙᴀss ʙᴏᴏsᴛ\n"
        "  → ʀᴀɴɢᴇ : 1 ᴛᴏ 20\n\n"
        "✦ /bassoff\n"
        "  → ᴛᴜʀɴ ᴏғғ ʙᴀss ʙᴏᴏsᴛ\n\n"
        "✦ /effecton\n"
        "  → ᴇɴᴀʙʟᴇ ᴇғғᴇᴄᴛs ғᴏʀ ᴛʜᴇ ɢʀᴏᴜᴘ\n\n"
        "✦ /effectoff\n"
        "  → ᴅɪsᴀʙʟᴇ ᴇғғᴇᴄᴛs ғᴏʀ ᴛʜᴇ ɢʀᴏᴜᴘ\n\n"
        "💡 ᴇxᴀᴍᴩʟᴇ :\n"
        "  <code>/speed 1.5</code>\n"
        "  <code>/bass 10</code>\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),

    "help_info": (
        "╔══════════════════════════════════════════╗\n"
        "║    ℹ️ ɪɴғᴏ ᴄᴏᴍᴍᴀɴᴅs                   ║\n"
        "╚══════════════════════════════════════════╝\n\n"
        "✦ /repo\n"
        "  → ɢᴇᴛ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ʟɪɴᴋ\n\n"
        "✦ /id\n"
        "  → ɢᴇᴛ ᴜsᴇʀ/ᴄʜᴀᴛ/ᴍsɢ IDs\n\n"
        "✦ /stats\n"
        "  → ғᴜʟʟ ʙᴏᴛ sᴛᴀᴛs (Owner only)\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    ),
}


@bot.on_callback_query()
async def callback_handler(_, query: CallbackQuery) -> None:
    user_id = query.from_user.id
    data = query.data

    if is_user_blocked_db(user_id):
        await query.answer("You are blocked from using this bot.", show_alert=True)
        return

    if data == "show_help":
        await query.message.edit_caption(
            caption=(
                "╔══════════════════════════════════════════╗\n"
                "║    💫 ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ʜᴇʟᴘ 💫          ║\n"
                "╚══════════════════════════════════════════╝\n\n"
                f"✦ ʜᴇʏ {query.from_user.mention},\n"
                "📜 ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ :\n\n"
                "◈ ── ── ── ── ── ── ── ◈\n"
                "  ⚡ ғᴀsᴛ • sᴍᴏᴏᴛʜ • ᴘᴏᴡᴇʀꜰᴜʟ\n"
                "◈ ── ── ── ── ── ── ── ◈\n\n"
                "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=_HELP_KB,
        )
        await query.answer()
        return

    if data == "go_back":
        await query.message.edit_caption(
            caption=(
                "╔══════════════════════════════════════════╗\n"
                "║    💫 ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ʜᴇʟᴘ 💫          ║\n"
                "╚══════════════════════════════════════════╝\n\n"
                f"✦ ʜᴇʏ {query.from_user.mention},\n"
                "📜 ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ :\n\n"
                "◈ ── ── ── ── ── ── ── ◈\n"
                "  ⚡ ғᴀsᴛ • sᴍᴏᴏᴛʜ • ᴘᴏᴡᴇʀꜰᴜʟ\n"
                "◈ ── ── ── ── ── ── ── ◈\n\n"
                "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=_HELP_KB,
        )
        await query.answer()
        return

    if data.startswith("help_"):
        text = _HELP_TEXTS.get(data)
        if text:
            await query.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=_BACK_KB,
            )
            await query.answer()
        else:
            await query.answer("Help topic not found.", show_alert=True)
        return

    if data == "close_help":
        await query.message.delete()
        await query.answer()
        return

    chat_id = query.message.chat.id

    if data == "pause":
        if not await is_user_authorized(query):
            await query.answer("Only admins can control playback!", show_alert=True)
            return
        try:
            await call_py.pause(chat_id)
            await query.answer("⏸️ Paused")
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)
        return

    if data == "resume":
        if not await is_user_authorized(query):
            await query.answer("Only admins can control playback!", show_alert=True)
            return
        try:
            await call_py.resume(chat_id)
            await query.answer("▶️ Resumed")
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)
        return

    if data == "skip":
        if not await is_user_authorized(query):
            await query.answer("Only admins can control playback!", show_alert=True)
            return
        if not queue_size(chat_id):
            await query.answer("Queue is empty!", show_alert=True)
            return

        skipped = pop_current(chat_id)
        try:
            await call_py.leave_call(chat_id)
        except Exception:
            pass
        await asyncio.sleep(1)

        nxt = peek_current(chat_id)
        if nxt:
            try:
                delete_file(skipped.get("file_path", ""))
            except Exception:
                pass
            await query.answer(f"⏭️ Skipped: {short(skipped['title'])}")
            msg = await bot.send_message(
                chat_id,
                f"🎵 ɴᴇxᴛ ᴛʀᴀᴄᴋ : <code>{nxt['title']}</code>",
                parse_mode=ParseMode.HTML,
            )
            await play_song(chat_id, msg, nxt)
        else:
            await leave_vc(chat_id)
            await query.answer("Queue finished, left VC")
        return

    if data == "stop":
        if not await is_user_authorized(query):
            await query.answer("Only admins can control playback!", show_alert=True)
            return
        await leave_vc(chat_id)
        await query.answer("⏹️ Stopped")
        return

    if data == "seek":
        if not await is_user_authorized(query):
            await query.answer("Only admins can control playback!", show_alert=True)
            return
        await query.answer("Use /seek <seconds> to forward", show_alert=True)
        return

    if data == "seekback":
        if not await is_user_authorized(query):
            await query.answer("Only admins can control playback!", show_alert=True)
            return
        await query.answer("Use /seekback <seconds> to rewind", show_alert=True)
        return

    if data == "back":
        await query.answer("Not implemented yet", show_alert=True)
        return

    if data == "loop":
        await query.answer("Loop feature coming soon!", show_alert=True)
        return

    if data == "effects_menu":
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚡ sᴘᴇᴇᴅ", callback_data="speed_menu"),
                InlineKeyboardButton("🎵 ʙᴀss", callback_data="bass_menu"),
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="show_help"),
            ],
        ])
        await query.message.edit_caption(
            caption=(
                "╔══════════════════════════════════════════╗\n"
                "║    🎵 ᴇғғᴇᴄᴛs ᴍᴇɴᴜ 🎵               ║\n"
                "╚══════════════════════════════════════════╝\n\n"
                "✦ ᴄʜᴏᴏsᴇ ᴀɴ ᴇғғᴇᴄᴛ :\n\n"
                "⚡ sᴘᴇᴇᴅ - ᴄʜᴀɴɢᴇ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ\n"
                "🎵 ʙᴀss - ᴀᴅᴅ ʙᴀss ʙᴏᴏsᴛ\n\n"
                "💡 ᴜsᴇ ᴄᴏᴍᴍᴀɴᴅs :\n"
                "  <code>/speed 1.5</code>\n"
                "  <code>/bass 10</code>\n\n"
                "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        await query.answer()
        return

    if data == "speed_menu":
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("0.5x", callback_data="speed_0.5"),
                InlineKeyboardButton("0.75x", callback_data="speed_0.75"),
                InlineKeyboardButton("1.0x", callback_data="speed_1.0"),
            ],
            [
                InlineKeyboardButton("1.25x", callback_data="speed_1.25"),
                InlineKeyboardButton("1.5x", callback_data="speed_1.5"),
                InlineKeyboardButton("2.0x", callback_data="speed_2.0"),
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="effects_menu"),
            ],
        ])
        await query.message.edit_caption(
            caption=(
                "╔══════════════════════════════════════════╗\n"
                "║    ⚡ sᴘᴇᴇᴅ ᴍᴇɴᴜ ⚡                   ║\n"
                "╚══════════════════════════════════════════╝\n\n"
                "✦ ᴄʜᴏᴏsᴇ sᴘᴇᴇᴅ :\n\n"
                "💡 ᴏʀ ᴜsᴇ ᴄᴏᴍᴍᴀɴᴅ :\n"
                "  <code>/speed 1.5</code>\n\n"
                "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        await query.answer()
        return

    if data.startswith("speed_"):
        try:
            speed = float(data.split("_")[1])
            await query.answer(f"⚡ Speed set to {speed}x")
        except Exception:
            await query.answer("Invalid speed!", show_alert=True)
        return

    if data == "bass_menu":
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("5", callback_data="bass_5"),
                InlineKeyboardButton("10", callback_data="bass_10"),
                InlineKeyboardButton("15", callback_data="bass_15"),
            ],
            [
                InlineKeyboardButton("20", callback_data="bass_20"),
                InlineKeyboardButton("OᴰF", callback_data="bass_off"),
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="effects_menu"),
            ],
        ])
        await query.message.edit_caption(
            caption=(
                "╔══════════════════════════════════════════╗\n"
                "║    🎵 ʙᴀss ᴍᴇɴᴜ 🎵                    ║\n"
                "╚══════════════════════════════════════════╝\n\n"
                "✦ ᴄʜᴏᴏsᴇ ʙᴀss ʙᴏᴏsᴛ :\n\n"
                "💡 ᴏʀ ᴜsᴇ ᴄᴏᴍᴍᴀɴᴅ :\n"
                "  <code>/bass 10</code>\n\n"
                "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        await query.answer()
        return

    if data.startswith("bass_"):
        try:
            if data == "bass_off":
                await query.answer("🎵 Bass turned off")
            else:
                bass = int(data.split("_")[1])
                await query.answer(f"🎵 Bass boost set to {bass}")
        except Exception:
            await query.answer("Invalid bass value!", show_alert=True)
        return

    if data == "noop":
        await query.answer()
        return

    await query.answer("Unknown action.", show_alert=True)
EOF
