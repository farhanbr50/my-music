cat > ChandMusic/core/call.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio

from pyrogram.enums import ParseMode
from pytgcalls.exceptions import NoActiveGroupCall
from ntgcalls import TelegramServerError

from ChandMusic import LOGGER, bot, call_py
from ChandMusic.core.autoplay import is_autoplay, maybe_refetch, stop_autoplay
from ChandMusic.core.queue import clear_queue, peek_current, pop_current
from ChandMusic.utils.helpers import delete_file


async def leave_vc(chat_id: int) -> None:
    try:
        stop_autoplay(chat_id)
    except Exception:
        pass

    for song in clear_queue(chat_id):
        try:
            delete_file(song.get("file_path", ""))
        except Exception:
            pass

    try:
        await call_py.leave_call(chat_id)
    except NoActiveGroupCall:
        pass
    except TelegramServerError as e:
        LOGGER.error(f"⚡ Leave VC TelegramServerError: {e}")
    except Exception as e:
        LOGGER.error(f"⚡ Leave VC Error: {e}")
EOF
