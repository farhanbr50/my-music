cat > ChandMusic/core/watcher.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio

from ChandMusic import LOGGER


async def watchdog():
    while True:
        try:
            LOGGER.info("🐾 Watchdog: Bot is healthy ✨")
        except Exception as e:
            LOGGER.error(f"⚡ Watchdog error: {e}")
        await asyncio.sleep(60)
EOF
