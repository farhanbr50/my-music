cat > ChandMusic/modules/ping.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import os
import time
from datetime import timedelta

import psutil
import speedtest
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ChandMusic import bot, assistant, bot_start_time
from ChandMusic.modules.block import user_allowed


def supp_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🍬 sᴜᴘᴘᴏʀᴛ 🍬", url=config.SUPPORT_GROUP)],
    ])


@bot.on_message(filters.command("ping") & user_allowed)
async def ping_cmd(client, message: Message) -> None:
    start = time.perf_counter()
    pm = await message.reply_text(
        f"✦ {client.me.first_name} ɪs ᴘɪɴɢɪɴɢ...",
        parse_mode=ParseMode.HTML,
    )
    latency = round((time.perf_counter() - start) * 1000)
    uptime = str(timedelta(seconds=int(time.time() - bot_start_time)))
    cpu = psutil.cpu_percent(interval=1)
    process = psutil.Process(os.getpid())
    ram = process.memory_info().rss / 1024 / 1024
    disk = psutil.disk_usage("/")
    disk_str = f"{disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB ({disk.percent}%)"

    try:
        pytg_start = time.perf_counter()
        await assistant.get_me()
        pytg = round((time.perf_counter() - pytg_start) * 1000)
    except Exception:
        pytg = "N/A"

    await pm.delete()

    caption = (
        f"🏓 ᴘᴏɴɢ : <code>{latency}ms</code>\n\n"
        f"✨ <u>{client.me.first_name} sʏsᴛᴇᴍ sᴛᴀᴛs :</u>\n\n"
        f"✦ ᴜᴘᴛɪᴍᴇ : <code>{uptime}</code>\n"
        f"✦ ʀᴀᴍ : <code>{ram:.2f} MB</code>\n"
        f"✦ ᴄᴘᴜ : <code>{cpu}%</code>\n"
        f"✦ ᴅɪsᴋ : <code>{disk_str}</code>\n"
        f"✦ ᴘʏᴛɢᴄ : <code>{pytg}ms</code>\n\n"
        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ⭐"
    )

    try:
        await message.reply_photo(
            photo=config.PING_IMG_URL,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=supp_markup(),
        )
    except Exception:
        await message.reply(
            caption,
            parse_mode=ParseMode.HTML,
            reply_markup=supp_markup(),
        )
EOF
