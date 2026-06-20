cat > ChandMusic/__init__.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import logging
import time

from pyrogram import Client
from pyrogram.enums import ParseMode
from pytgcalls import PyTgCalls

import config

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="[%(levelname)s] %(asctime)s — %(name)s — %(message)s",
    level=logging.INFO,
)

print("""
╔══════════════════════════════════════════╗
║    ✨ ᴄʜᴀɴᴅ ᴍᴜsɪᴄ ✨                 ║
║   ⭐ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜᴀɴᴅ  ⭐            ║
║   🎵 ʀᴇᴀᴅʏ ᴛᴏ ᴘʟᴀʏ!                  ║
╚══════════════════════════════════════════╝
""")

bot = Client(
    name=config.SESSION_NAME,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    max_concurrent_transmissions=10,
)

assistant = Client(
    name=f"{config.SESSION_NAME}_assistant",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.STRING_SESSION,
    parse_mode=ParseMode.HTML,
    max_concurrent_transmissions=10,
)

call_py = PyTgCalls(assistant, cache_duration=180)
bot_start_time = time.time()
EOF
