from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from plugins.database import db
from pyrogram import Client, filters
from config import ADMINS
import asyncio
import datetime
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        # ⚠️ DELETE MAT KARO — ye sirf iska matlab hai bot ne
        # is user se pehle kabhi baat nahi ki (cache miss).
        # Redeploy ke baad ye common hai. User DB mein rehega.
        logging.info(f"{user_id} - PeerIdInvalid (skipped, not deleted)")
        return False, "PeerInvalid"
    except Exception as e:
        return False, "Error"


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def verupikkals(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    peer_invalid = 0  # NEW: alag counter

    success = 0
    async for user in users:
        if 'id' in user:
            pti, sh = await broadcast_messages(int(user['id']), b_msg)
            if pti:
                success += 1
            elif pti == False:
                if sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                elif sh == "PeerInvalid":
                    peer_invalid += 1  # sirf count karo, delete nahi
                elif sh == "Error":
                    failed += 1
            done += 1
            if not done % 20:
                await sts.edit(
                    f"Broadcast in progress:\n\n"
                    f"Total Users: {total_users}\n"
                    f"Completed: {done} / {total_users}\n"
                    f"✅ Success: {success}\n"
                    f"🚫 Blocked: {blocked}\n"
                    f"❌ Deleted: {deleted}\n"
                    f"⚠️ PeerInvalid (skipped): {peer_invalid}"
                )
        else:
            done += 1
            failed += 1

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"✅ Broadcast Completed in {time_taken}\n\n"
        f"Total Users: {total_users}\n"
        f"Completed: {done} / {total_users}\n"
        f"✅ Success: {success}\n"
        f"🚫 Blocked: {blocked}\n"
        f"❌ Deleted: {deleted}\n"
        f"⚠️ PeerInvalid (skipped): {peer_invalid}\n"
        f"💥 Other Errors: {failed}"
    )
