cat > ChandMusic/utils/assistant.py << 'EOF'
# --------------------------------------------------------------------------------
#  ✨ ChandMusic © 2026 ✨
#  Developed by Chand ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

from pyrogram.enums import ParseMode

from ChandMusic import assistant, bot


async def is_assistant_in(chat_id: int):
    try:
        me = await assistant.get_me()
        member = await assistant.get_chat_member(chat_id, me.id)
        return member.status is not None
    except Exception as e:
        err = str(e)
        if "USER_BANNED" in err or "Banned" in err:
            return "banned"
        return False


async def try_join_assistant(chat_id: int, pm) -> bool:
    try:
        invite_link = await bot.export_chat_invite_link(chat_id)

        if invite_link.startswith("https://t.me/+"):
            invite_link = invite_link.replace(
                "https://t.me/+",
                "https://t.me/joinchat/",
            )

        await assistant.join_chat(invite_link)
        return True

    except Exception as e:
        await pm.edit_text(
            f"⚡ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴ ғᴀɪʟᴇᴅ\n<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return False
EOF
