cat > ChandMusic/modules/stats.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import platform
import sys

import psutil
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ChandMusic import bot
from ChandMusic.utils.db import (
    get_mongo_client,
    get_served_chats_count,
    get_served_users_count,
    get_banned_chats_count,
    get_total_plays,
    get_broadcast_count,
    is_connected,
)


@bot.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def stats_cmd(_, message: Message) -> None:
    processing = await message.reply(
        "✦ Fetching stats, please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        freq_str = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
        p_cores = psutil.cpu_count(logical=False) or "N/A"
        t_cores = psutil.cpu_count(logical=True) or "N/A"
        ram = psutil.virtual_memory()
        ram_total = ram.total / (1024 ** 3)
        ram_used = ram.used / (1024 ** 3)
        ram_free = ram.available / (1024 ** 3)
        ram_percent = ram.percent
        hdd = psutil.disk_usage("/")
        disk_total = hdd.total / (1024 ** 3)
        disk_used = hdd.used / (1024 ** 3)
        disk_free = hdd.free / (1024 ** 3)
        disk_percent = hdd.percent
        py_version = sys.version.split()[0]
        os_name = platform.system()
        os_release = platform.release()
    except Exception as e:
        await processing.edit_text(
            f"⚡ System stats error: <code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    db_line = "✦ MongoDB : <code>Not connected</code>"
    if is_connected():
        try:
            client = get_mongo_client()
            db_stats = client["ChandMusic"].command("dbstats")
            data_kb = db_stats.get("dataSize", 0) / 1024
            stor_kb = db_stats.get("storageSize", 0) / 1024
            col_cnt = db_stats.get("collections", 0)
            obj_cnt = db_stats.get("objects", 0)
            db_line = (
                f"✦ MongoDB : <code>Connected</code>\n"
                f"✦ Data     : <code>{data_kb:.2f} KB</code>\n"
                f"✦ Storage  : <code>{stor_kb:.2f} KB</code>\n"
                f"✦ Collections : <code>{col_cnt}</code>\n"
                f"✦ Objects  : <code>{obj_cnt}</code>"
            )
        except Exception as e:
            db_line = f"⚡ MongoDB error: <code>{e}</code>"

    chat_count = get_served_chats_count()
    user_count = get_served_users_count()
    banned_count = get_banned_chats_count()
    total_plays = get_total_plays()
    broadcast = get_broadcast_count()
    broadcast_line = (
        f"✦ Total     : <code>{broadcast['total']}</code>\n"
        f"✦ Private   : <code>{broadcast['private']}</code>\n"
        f"✦ Groups    : <code>{broadcast['groups']}</code>"
    )

    caption = (
        f"✨ <u>ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ꜱᴛᴀᴛꜱ</u>\n\n"

        f"💻 <u>ꜱʏꜱᴛᴇᴍ</u>\n"
        f"✦ ᴏꜱ : <code>{os_name} {os_release}</code>\n"
        f"✦ ᴘʏᴛʜᴏɴ : <code>{py_version}</code>\n"
        f"✦ ᴄᴘᴜ : <code>{cpu_percent}%</code> | Freq: <code>{freq_str}</code>\n"
        f"✦ ᴄᴏʀᴇꜱ : <code>{p_cores} Physical / {t_cores} Logical</code>\n"
        f"✦ ʀᴀᴍ : <code>{ram_used:.2f}GB / {ram_total:.2f}GB ({ram_percent}%)</code>\n"
        f"✦ ᴅɪꜱᴋ : <code>{disk_used:.2f}GB / {disk_total:.2f}GB ({disk_percent}%)</code>\n\n"

        f"📊 <u>ᴜꜱᴀɢᴇ</u>\n"
        f"✦ ᴄʜᴀᴛꜱ : <code>{chat_count}</code>\n"
        f"✦ ᴜꜱᴇʀꜱ : <code>{user_count}</code>\n"
        f"✦ ʙᴀɴɴᴇᴅ : <code>{banned_count}</code>\n"
        f"✦ ᴛᴏᴛᴀʟ ᴘʟᴀʏꜱ : <code>{total_plays}</code>\n\n"

        f"📢 <u>ʙʀᴏᴀᴅᴄᴀꜱᴛ</u>\n{broadcast_line}\n\n"

        f"🍃 <u>ᴍᴏɴɢᴏᴅʙ</u>\n{db_line}\n\n"

        "⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ ᴍᴜꜱɪᴄ ⭐"
    )

    await processing.edit_text(caption, parse_mode=ParseMode.HTML)
EOF
