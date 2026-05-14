import asyncio
from pyrogram import Client, filters, enums
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE, ADMINS
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Name - {}</b>
"""

# Default welcome text (jab tak admin ne custom set na kiya ho)
DEFAULT_WELCOME = (
    "<b>Hello {mention}! 👋\n"
    "Welcome To {chat_title}\n\n"
    "📢 Hamare updates pane ke liye neeche button dabao!\n\n"
    "<i>Powered By : @SuhaniBots</i></b>"
)


# ─────────────────────────────────────────────
#  /start
# ─────────────────────────────────────────────
@Client.on_message(filters.command('start'))
async def start_message(c, m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
    await m.reply_photo(
        "https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=(
            f"<b>Hello {m.from_user.mention} 👋\n\n"
            "I Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Requests.\n\n"
            "For All Pending Join Requests Use - /accept\n\n"
            "<i>Powered By : @SuhaniBots</i></b>"
        ),
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🤖 Update Channel", url="https://t.me/SuhaniBots")
            ]]
        )
    )


# ─────────────────────────────────────────────
#  /setwelcome  — admin welcome text set kare
#
#  Usage:
#    /setwelcome
#    Aapka naya welcome message yahan likho
#
#  Variables jo use kar sakte ho:
#    {mention}    → user ka mention
#    {first_name} → user ka naam
#    {chat_title} → group ka naam
# ─────────────────────────────────────────────
@Client.on_message(filters.command('setwelcome') & filters.user(ADMINS) & filters.private)
async def set_welcome(client, message):
    # Command ke baad wala text lo
    text_parts = message.text.split(None, 1)
    if len(text_parts) < 2 or not text_parts[1].strip():
        await message.reply(
            "<b>📝 Welcome message set karne ka tarika:</b>\n\n"
            "<code>/setwelcome Aapka message yahan</code>\n\n"
            "<b>Variables:</b>\n"
            "• <code>{mention}</code> → user mention\n"
            "• <code>{first_name}</code> → user ka naam\n"
            "• <code>{chat_title}</code> → group ka naam\n\n"
            "<b>Example:</b>\n"
            "<code>/setwelcome Hello {mention}! 👋\nWelcome karo hamari family mein!</code>"
        )
        return

    new_text = text_parts[1].strip()
    await db.set_welcome_text(new_text)
    await message.reply(
        f"✅ <b>Welcome message save ho gaya!</b>\n\n"
        f"<b>Preview:</b>\n{new_text.format(mention='@TestUser', first_name='Test', chat_title='YourGroup')}"
    )


# ─────────────────────────────────────────────
#  /editwelcome — already bheje gaye pinned
#                welcome messages bulk edit karo
#
#  Ye command sirf ADMIN ke bot DM mein chalega.
#  Bot DB mein stored har user ke pinned_msg_id
#  use karke unka message edit karega.
# ─────────────────────────────────────────────
@Client.on_message(filters.command('editwelcome') & filters.user(ADMINS) & filters.private)
async def edit_welcome(client, message):
    text_parts = message.text.split(None, 1)
    if len(text_parts) < 2 or not text_parts[1].strip():
        await message.reply(
            "<b>✏️ Purane welcome messages edit karne ka tarika:</b>\n\n"
            "<code>/editwelcome Naya message text</code>\n\n"
            "<b>Variables:</b>\n"
            "• <code>{mention}</code> → user mention\n"
            "• <code>{first_name}</code> → user ka naam\n\n"
            "⚠️ Sirf unhi users ka message edit hoga jinka\n"
            "pinned_msg_id DB mein saved hai."
        )
        return

    new_text = text_parts[1].strip()
    sts = await message.reply("✏️ Editing shuru ho raha hai...")

    users = db.col.find({'pinned_msg_id': {'$exists': True, '$ne': None}})
    total = 0
    success = 0
    failed = 0
    skipped = 0

    bot_username = (await client.get_me()).username

    async for user in users:
        # pinned_msg_id check karo — agar missing ya None hai toh skip karo
        pinned_id = user.get('pinned_msg_id')
        if not pinned_id:
            skipped += 1
            continue

        total += 1
        try:
            user_mention = f"<a href='tg://user?id={user['id']}'>{user.get('name', 'User')}</a>"
            formatted_text = new_text.format(
                mention=user_mention,
                first_name=user.get('name', 'User')
            )

            # Step 1: Purana message delete karo (silently)
            try:
                await client.delete_messages(
                    chat_id=int(user['id']),
                    message_ids=int(pinned_id)
                )
            except Exception:
                pass

            # Step 2: Naya message bhejo — user ko notification aayega
            new_msg = await client.send_message(
                chat_id=int(user['id']),
                text=formatted_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🤖 Start Bot & Get Updates",
                        url=f"https://t.me/{bot_username}?start=welcome")]]
                )
            )

            # Step 3: Naye message ka ID DB mein update karo
            await db.col.update_one(
                {'id': user['id']},
                {'$set': {'pinned_msg_id': new_msg.id}}
            )

            success += 1
        except Exception as e:
            failed += 1

        if total % 20 == 0:
            await sts.edit(
                f"✏️ Editing in progress...\n\n"
                f"Done: {total}\nSuccess: {success}\nFailed: {failed}\nSkipped: {skipped}"
            )
        await asyncio.sleep(0.3)  # flood wait se bachne ke liye

    await sts.edit(
        f"✅ <b>Edit Complete!</b>\n\n"
        f"Total: {total}\nSuccess: {success}\nFailed: {failed}\nSkipped: {skipped}"
    )


# ─────────────────────────────────────────────
#  /accept
# ─────────────────────────────────────────────
@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**For Accepting Pending Requests You Have To /login First.**")
        return
    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
    show = await show.edit(
        "**Now Forward A Message From Your Channel Or Group With Forward Tag\n\n"
        "Make Sure Your Logged In Account Is Admin In That Channel Or Group With Full Rights.**"
    )
    vj = await client.listen(message.chat.id)
    if vj.forward_from_chat and vj.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        try:
            info = await acc.get_chat(chat_id)
        except:
            await show.edit("**Error - Make Sure Your Logged In Account Is Admin In This Channel Or Group With Rights.**")
    else:
        return await message.reply("**Message Not Forwarded From Channel Or Group.**")
    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests. ✅**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** {str(e)}")


# ─────────────────────────────────────────────
#  Auto-approve new join requests
#  + Welcome message bhejo + Pin karo
# ─────────────────────────────────────────────
@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if NEW_REQ_MODE == False:
        return
    try:
        # DB mein add karo ya naam update karo
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
        else:
            # Purane user ka naam update karo — editwelcome ke liye zaroori hai
            await db.update_user_name(m.from_user.id, m.from_user.first_name)

        await client.approve_chat_join_request(m.chat.id, m.from_user.id)

        # Welcome text — DB se lo, warna default use karo
        saved_text = await db.get_welcome_text()
        welcome_template = saved_text if saved_text else DEFAULT_WELCOME

        formatted_text = welcome_template.format(
            mention=m.from_user.mention,
            first_name=m.from_user.first_name or "User",
            chat_title=m.chat.title or "Group"
        )

        try:
            bot_username = (await client.get_me()).username

            # ── Welcome message bhejo ──
            sent_msg = await client.send_message(
                m.from_user.id,
                formatted_text,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "🤖 Start Bot & Get Updates",
                            url=f"https://t.me/{bot_username}?start=welcome"
                        )
                    ]]
                )
            )

            # ── Us message ko pin karo (bot DM mein) ──
            try:
                await client.pin_chat_message(
                    chat_id=m.from_user.id,
                    message_id=sent_msg.id,
                    disable_notification=True  # Silent pin — user ko extra notification nahi aayega
                )
            except Exception:
                pass  # Agar pin na ho paye toh silently skip

            # ── Message ID DB mein save karo (baad mein edit ke liye) ──
            await db.col.update_one(
                {'id': m.from_user.id},
                {'$set': {'pinned_msg_id': sent_msg.id}}
            )

        except Exception:
            # User ne privacy lock kiya ho toh skip
            pass

    except Exception as e:
        print(str(e))
        pass
