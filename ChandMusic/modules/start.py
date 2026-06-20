cat > ChandMusic/modules/start.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import random

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ChandMusic import bot
from config import START_ANIMATIONS
from ChandMusic.modules.block import user_allowed
from ChandMusic.utils.db import (
    add_broadcast_chat,
    add_served_chat,
    add_served_user,
    load_welcome_state,
    save_welcome_state,
)
from ChandMusic.utils.permissions import is_user_authorized

EFFECT_ID = [
    5046509860389126442,
    5107584321108051014,
]

_welcome_cache: dict[int, bool] = {}


def is_welcome_enabled(chat_id: int) -> bool:
    if chat_id not in _welcome_cache:
        _welcome_cache[chat_id] = load_welcome_state(chat_id)
    return _welcome_cache.get(chat_id, True)


def set_welcome_state(chat_id: int, enabled: bool) -> None:
    _welcome_cache[chat_id] = enabled
    save_welcome_state(chat_id, enabled)


@bot.on_message(filters.command("start") & user_allowed)
async def start_handler(_, message: Message) -> None:
    uid = message.from_user.id
    name = message.from_user.first_name or "User"
    chat_id = message.chat.id
    chat_type = message.chat.type
    animation = random.choice(START_ANIMATIONS)

    try:
        await message.delete()
    except Exception:
        pass

    try:
        add_served_user(uid)
        add_served_chat(chat_id)
    except Exception:
        pass

    if chat_type == ChatType.PRIVATE:
        caption = (
            "╔══════════════════════════════════════════╗\n"
            "║    ✨ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ✨                 ║\n"
            "║    ⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ⭐            ║\n"
            "╚══════════════════════════════════════════╝\n\n"
            f"✦ ʜᴇʏ <a href='tg://user?id={uid}'>{name}</a>,\n"
            "💫 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ!\n\n"
            "◈ ── ── ── ── ── ── ── ◈\n"
            "  🎵 ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ\n"
            "  🎶 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ\n"
            "  ⚡ ғᴀsᴛ • sᴍᴏᴏᴛʜ • ᴘᴏᴡᴇʀꜰᴜʟ\n"
            "◈ ── ── ── ── ── ── ── ◈\n\n"
            "📌 ᴜsᴇ <code>/help</code> ꜰᴏʀ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs\n\n"
            "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
        )
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🎵 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                    url=f"{config.BOT_LINK}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton("🍬 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
                InlineKeyboardButton("🍹 ᴜᴘᴅᴀᴛᴇs", url=config.UPDATES_CHANNEL),
            ],
            [
                InlineKeyboardButton("🏩 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="show_help"),
            ],
            [
                InlineKeyboardButton("🫧 ᴏᴡɴᴇʀ", url=f"tg://user?id={config.OWNER_ID}"),
                InlineKeyboardButton("🍡 sᴏᴜʀᴄᴇ", url="https://github.com/Chand/ChandMusic"),
            ],
        ])

        sent = await message.reply_animation(
            animation,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
            message_effect_id=random.choice(EFFECT_ID),
        )

        try:
            add_broadcast_chat(chat_id, "private")
        except Exception:
            pass

        if config.LOGGER_ID:
            try:
                await bot.send_message(
                    config.LOGGER_ID,
                    "✨ #ɴᴇᴡᴜsᴇʀ sᴛᴀʀᴛᴇᴅ ✨\n\n"
                    f"✦ ɴᴀᴍᴇ     : <a href='tg://user?id={uid}'>{name}</a>\n"
                    f"✦ ɪᴅ       : <code>{uid}</code>\n"
                    f"✦ ᴜsᴇʀɴᴀᴍᴇ : @{message.from_user.username or 'N/A'}",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass

    else:
        chat_title = message.chat.title or "ᴛʜɪs ᴄʜᴀᴛ"
        caption = (
            f"✦ ʜᴇʏ <a href='tg://user?id={uid}'>{name}</a>,\n"
            f"💫 ᴛʜɪs ɪs <b>{config.BOT_NAME}</b>\n\n"
            f"🎵 ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ <b>{chat_title}</b>\n"
            f"⚡ {name} ᴄᴀɴ ɴᴏᴡ ᴘʟᴀʏ sᴏɴɢs ʜᴇʀᴇ."
        )
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🎵 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                    url=f"{config.BOT_LINK}?startgroup=true"
                ),
                InlineKeyboardButton("🍬 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
            ],
            [
                InlineKeyboardButton("🏩 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="show_help"),
            ],
        ])

        sent = await message.reply_animation(
            animation,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )

        admin_msg = (
            "╔══════════════════════════════════════════╗\n"
            "║    ⚡ ᴀᴅᴍɪɴ ʀᴇϙᴜɪʀᴇᴅ ⚡              ║\n"
            "╚══════════════════════════════════════════╝\n\n"
            "🌸 ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ!\n\n"
            "◈ ── ── ── ── ── ── ── ◈\n"
            "📌 ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ\n"
            "📌 ᴡɪᴛʜ ᴛʜᴇsᴇ ᴘᴇʀᴍɪssɪᴏɴs:\n"
            "◈ ── ── ── ── ── ── ── ◈\n"
            "  ✅ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs\n"
            "  ✅ ᴍᴀɴᴀɢᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs\n"
            "  ✅ ɪɴᴠɪᴛᴇ ᴜsᴇʀs\n"
            "◈ ── ── ── ── ── ── ── ◈\n\n"
            "⚠️ ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴍɪɴ ᴘᴇʀᴍs\n"
            "🚫 sᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs ᴡᴏɴ'ᴛ ᴡᴏʀᴋ!\n\n"
            "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
        )
        admin_kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⚡ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ",
                    url=f"tg://user?id={(await bot.get_me()).id}",
                )
            ]
        ])
        try:
            admin_sent = await message.reply_text(
                admin_msg,
                parse_mode=ParseMode.HTML,
                reply_markup=admin_kb,
            )
        except Exception:
            pass

        try:
            add_broadcast_chat(chat_id, "group")
        except Exception:
            pass


@bot.on_message(filters.command("help") & user_allowed)
async def help_handler(_, message: Message) -> None:
    uid = message.from_user.id
    name = message.from_user.first_name or "User"

    try:
        await message.delete()
    except Exception:
        pass

    kb = InlineKeyboardMarkup([
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
            InlineKeyboardButton("⌯ ᴄʟᴏsᴇ ⌯", callback_data="close_help"),
        ],
    ])

    animation = random.choice(START_ANIMATIONS)

    sent = await message.reply_animation(
        animation,
        caption=(
            "╔══════════════════════════════════════════╗\n"
            "║    💫 ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ʜᴇʟᴘ 💫          ║\n"
            "╚══════════════════════════════════════════╝\n\n"
            f"✦ ʜᴇʏ <a href='tg://user?id={uid}'>{name}</a>,\n"
            "📜 ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ :\n\n"
            "◈ ── ── ── ── ── ── ── ◈\n"
            "  ⚡ ғᴀsᴛ • sᴍᴏᴏᴛʜ • ᴘᴏᴡᴇʀꜰᴜʟ\n"
            "◈ ── ── ── ── ── ── ── ◈\n\n"
            "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
    )


@bot.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(_, message: Message) -> None:
    chat_id = message.chat.id

    if not is_welcome_enabled(chat_id):
        return

    for member in message.new_chat_members:
        if member.id == (await bot.get_me()).id:
            continue

        name = member.first_name or "User"
        mention = member.mention

        # Get profile photo
        photo_url = None
        try:
            if member.photo:
                photo_url = await bot.download_media(member.photo.big_file_id)
        except Exception:
            pass

        caption = (
            "╔══════════════════════════════════════════╗\n"
            "║    ✨ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ✨                 ║\n"
            "║  🌙 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ғᴀᴍɪʟʏ 🌙      ║\n"
            "╚══════════════════════════════════════════╝\n\n"
            f"🌸 ʜᴇʏ {mention},\n"
            "💫 ᴛʜᴀɴᴋs ꜰᴏʀ ᴊᴏɪɴɪɴɢ ᴛʜɪs ɢʀᴏᴜᴘ!\n\n"
            "◈ ── ── ── ── ── ── ── ◈\n"
            "  🎶 ᴇɴᴊᴏʏ ᴍᴜsɪᴄ ᴡɪᴛʜ ᴜs\n"
            "  ⚡ ғᴀsᴛ • sᴍᴏᴏᴛʜ • ᴘᴏᴡᴇʀꜰᴜʟ\n"
            "◈ ── ── ── ── ── ── ── ◈\n\n"
            "📌 ᴜsᴇ <code>/help</code> ꜰᴏʀ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs\n"
            "📌 ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ <code>/welcome off</code> ᴛᴏ ᴅɪsᴀʙʟᴇ\n\n"
            "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
        )

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🎵 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                    url=config.BOT_LINK
                ),
            ],
            [
                InlineKeyboardButton("🍬 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
                InlineKeyboardButton("🍹 ᴜᴘᴅᴀᴛᴇs", url=config.UPDATES_CHANNEL),
            ],
            [
                InlineKeyboardButton("🌙 ᴄʜᴀɴᴅ ᴍᴜsɪᴄ", url="https://github.com/Chand/ChandMusic"),
            ],
        ])

        try:
            await message.reply_photo(
                photo=photo_url if photo_url else "https://telegra.ph/file/1a3c152717eb9d2e94dc2.mp4",
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
            )
        except Exception:
            await message.reply(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
                disable_web_page_preview=True,
            )


@bot.on_message(filters.command("welcome") & filters.group)
async def welcome_toggle_cmd(_, message: Message) -> None:
    chat_id = message.chat.id

    if not await is_user_authorized(message):
        await message.reply(
            "⚡ ᴀᴅᴍɪɴ ᴏɴʟʏ\n"
            "✦ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ",
            parse_mode=ParseMode.HTML,
        )
        return

    args = message.command[1:] if message.command else []

    if not args:
        state = is_welcome_enabled(chat_id)
        await message.reply(
            f"✦ ᴡᴇʟᴄᴏᴍᴇ sᴛᴀᴛᴜs : <code>{'✅ ᴏɴ' if state else '❌ ᴏꜰꜰ'}</code>\n\n"
            "✦ ᴜsᴀɢᴇ :\n"
            "<code>/welcome on</code>  → ᴇɴᴀʙʟᴇ\n"
            "<code>/welcome off</code> → ᴅɪsᴀʙʟᴇ",
            parse_mode=ParseMode.HTML,
        )
        return

    cmd = args[0].lower()
    if cmd == "on":
        set_welcome_state(chat_id, True)
        await message.reply(
            "╔══════════════════════════════════════════╗\n"
            "║    ✅ ᴡᴇʟᴄᴏᴍᴇ ᴇɴᴀʙʟᴇᴅ ✅            ║\n"
            "╚══════════════════════════════════════════╝\n\n"
            "🌸 ɴᴇᴡ ᴍᴇᴍʙᴇʀs ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ᴀ ᴡᴀʀᴍ ᴡᴇʟᴄᴏᴍᴇ!",
            parse_mode=ParseMode.HTML,
        )
    elif cmd == "off":
        set_welcome_state(chat_id, False)
        await message.reply(
            "╔══════════════════════════════════════════╗\n"
            "║    ❌ ᴡᴇʟᴄᴏᴍᴇ ᴅɪsᴀʙʟᴇᴅ ❌           ║\n"
            "╚══════════════════════════════════════════╝\n\n"
            "🌸 ɴᴇᴡ ᴍᴇᴍʙᴇʀs ᴡɪʟʟ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ᴀ ᴡᴇʟᴄᴏᴍᴇ.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply(
            "✦ ɪɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ\n"
            "✦ ᴜsᴇ : <code>/welcome on</code> ᴏʀ <code>/welcome off</code>",
            parse_mode=ParseMode.HTML,
        )
EOF
