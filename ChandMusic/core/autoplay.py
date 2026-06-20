cat > ChandMusic/core/autoplay.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import random

from ChandMusic import LOGGER, bot
from ChandMusic.core.queue import add_to_queue, peek_current
from ChandMusic.utils.youtube import search_yt

_autoplay_status: dict[int, bool] = {}
_autoplay_query: dict[int, str] = {}
_autoplay_fetching: dict[int, bool] = {}
_autoplay_loop_task: dict[int, asyncio.Task] = {}


def is_autoplay(chat_id: int) -> bool:
    return _autoplay_status.get(chat_id, False)


def get_autoplay_query(chat_id: int) -> str:
    return _autoplay_query.get(chat_id, "")


def start_autoplay(chat_id: int, query: str, requester: str, requester_id: int) -> int:
    _autoplay_status[chat_id] = True
    _autoplay_query[chat_id] = query

    count = 0
    try:
        search_query = f"{query} random"
        result = asyncio.run(search_yt(search_query))
        if result and isinstance(result, tuple):
            url, title, duration, thumb = result
            song = {
                "url": url,
                "title": title,
                "duration": duration,
                "requester": requester,
                "requester_id": requester_id,
                "thumbnail": thumb,
                "video": False,
            }
            add_to_queue(chat_id, song)
            count += 1

            for _ in range(2):
                result = asyncio.run(search_yt(f"{query} song"))
                if result and isinstance(result, tuple):
                    url, title, duration, thumb = result
                    song = {
                        "url": url,
                        "title": title,
                        "duration": duration,
                        "requester": requester,
                        "requester_id": requester_id,
                        "thumbnail": thumb,
                        "video": False,
                    }
                    add_to_queue(chat_id, song)
                    count += 1
    except Exception as e:
        LOGGER.error(f"⚡ [AutoPlay] Error: {e}")

    _autoplay_fetching[chat_id] = False
    return count


def stop_autoplay(chat_id: int) -> None:
    _autoplay_status[chat_id] = False
    if chat_id in _autoplay_loop_task:
        _autoplay_loop_task[chat_id].cancel()
        del _autoplay_loop_task[chat_id]


async def maybe_refetch(chat_id: int, query: str, _: int) -> None:
    if not is_autoplay(chat_id):
        return

    if _autoplay_fetching.get(chat_id, False):
        return

    current_queue = peek_current(chat_id)
    if current_queue:
        return

    _autoplay_fetching[chat_id] = True
    try:
        search_query = f"{query} song"
        result = await search_yt(search_query)
        if result and isinstance(result, tuple):
            url, title, duration, thumb = result
            song = {
                "url": url,
                "title": title,
                "duration": duration,
                "requester": "AutoPlay",
                "requester_id": 0,
                "thumbnail": thumb,
                "video": False,
            }
            add_to_queue(chat_id, song)
    except Exception as e:
        LOGGER.error(f"⚡ [AutoPlay] Refetch error: {e}")
    finally:
        _autoplay_fetching[chat_id] = False
EOF
