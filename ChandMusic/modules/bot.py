cat > ChandMusic/modules/bot.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ChandMusic import bot
from ChandMusic.utils.db import add_broadcast_chat, add_served_chat, remove_broadcast_chat, remove_served_chat


@bot.on_message(filters.new_chat_members, group=-10)
async def bot_added_watcher(_, message: Message) -> None:
    try:
        chat = message.chat
        chat_id = chat.id
        me = await bot.get_me()

        for member in message.new_chat_members:
            if member.id != me.id:
                continue

            add_served_chat(chat_id)
            add_broadcast_chat(chat_id, "group")

            admin_request_text = (
                "╔══════════════════════════════════════════╗\n"
                "║    ⚡ ᴀᴅᴍɪɴ ʀᴇϙᴜɪʀᴇᴅ ⚡              ║\n"
                "╚══════════════════════════════════════════╝\n\n"
                "🌸 ᴛʜᴀɴᴋs ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ!\n\n"
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
                [InlineKeyboardButton("⚡ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ", url=f"tg://user?id={me.id}")]
            ])
            try:
                await message.reply_text(admin_request_text, parse_mode=ParseMode.HTML, reply_markup=admin_kb)
            except Exception:
                pass

    except Exception as e:
        print(f"⚡ [watcher] bot_added_watcher error: {e}")


@bot.on_message(filters.left_chat_member, group=-12)
async def bot_left_watcher(_, message: Message) -> None:
    try:
        left_member = message.left_chat_member
        if not left_member:
            return

        me = await bot.get_me()
        if left_member.id != me.id:
            return

        chat_id = message.chat.id

        remove_served_chat(chat_id)
        remove_broadcast_chat(chat_id)

    except Exception as e:
        print(f"⚡ [watcher] bot_left_watcher error: {e}")
EOF
