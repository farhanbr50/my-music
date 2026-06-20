cat > config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

API_ID          = int(os.environ["API_ID"])
API_HASH        = os.environ["API_HASH"]
BOT_TOKEN       = os.environ["BOT_TOKEN"]
STRING_SESSION  = os.environ["STRING_SESSION"]
MONGO_DB_URL    = os.environ["MONGO_DB_URL"]
OWNER_ID        = int(os.environ["OWNER_ID"])

BOT_NAME         = os.getenv("BOT_NAME", "✨ Chand Music ✨")
BOT_LINK         = os.getenv("BOT_LINK", "https://t.me/ChandMusicBot")
UPDATES_CHANNEL  = os.getenv("UPDATES_CHANNEL", "https://t.me/CHAND_UPDATE")
SUPPORT_GROUP    = os.getenv("SUPPORT_GROUP", "https://t.me/CHANDCHATS")
LOGGER_ID        = int(os.getenv("LOGGER_ID", "0"))
PING_IMG_URL     = os.getenv("PING_IMG_URL", "https://files.catbox.moe/ddzvc0.jpg")
SESSION_NAME     = os.getenv("SESSION_NAME", "ChandMusic")
PORT             = int(os.getenv("PORT", 10000))

START_ANIMATIONS = [
    "https://telegra.ph/file/1a3c152717eb9d2e94dc2.mp4",
    "https://graph.org/file/ba7699c28dab379b518ca.mp4",
]

MAX_DURATION_SECONDS = 1800
QUEUE_LIMIT          = 20
COOLDOWN             = 10
EOF
