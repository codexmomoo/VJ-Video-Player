import random
import requests
import humanize
import base64
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from info import LOG_CHANNEL, LINK_URL, ADMIN
from plugins.database import checkdb, db, get_count, get_withdraw, record_withdraw, record_visit
from urllib.parse import quote_plus, urlencode
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes

async def encode(string):
    try:
        string_bytes = string.encode("ascii")
        base64_bytes = base64.urlsafe_b64encode(string_bytes)
        base64_string = (base64_bytes.decode("ascii")).strip("=")
        return base64_string
    except:
        pass

async def decode(base64_string):
    try:
        base64_string = base64_string.strip("=")
        base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes) 
        string = string_bytes.decode("ascii")
        return string
    except:
        pass

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await checkdb.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        name = await client.ask(message.chat.id, "<b>Welcome To CodeX OTT.\n\nLet's Create Your Account!\n\nSend Me Your Business Name Which Will Show On Website\nEx :- <code>CodeX OTT</code></b>")
        if name.text:
            await db.set_name(message.from_user.id, name=name.text)
        else:
            return await message.reply("**Wrong Input! Start Again By Hitting /start**")
        link = await client.ask(message.chat.id, "<b>Now Send Me Your Telegram Channel Link. It Will Show On Your Website.\n\nSend Like This <code>https://t.me/CODExMOMO</code> ✅\n\nDo Not Send Like This @CODExMOMO ❌</b>")
        if link.text and link.text.startswith(('http://', 'https://')):
            await db.set_link(message.from_user.id, link=link.text)
        else:
            return await message.reply("**Wrong Input! Start Again By Hitting /start**")
        await checkdb.add_user(message.from_user.id, message.from_user.first_name)
        return await message.reply("<b>Congratulations 🎉\n\nYour Account Created Successfully!\n\nTo Upload File With Quality Options Use /quality\n\nOther Commands: /account | /update | /withdraw\n\nFor Direct Upload Without Quality Option — Just Send File To Bot.</b>")
    else:
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Join CodeX OTT", url="https://t.me/CODExMOMO")]])
        await client.send_message(
            chat_id=message.from_user.id,
            text=script.START_TXT.format(message.from_user.mention),
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )
        return

@Client.on_message(filters.command("update") & filters.private)
async def update(client, message):
    vj = True
    if vj:
        name = await client.ask(message.chat.id, "<b>Send Me Your Business Name Which Will Show On Website\nEx :- <code>CodeX OTT</code>\n\n/cancel - Cancel The Process</b>")
        if name.text == "/cancel":
            return await message.reply("**Process Cancelled**")
        if name.text:
            await db.set_name(message.from_user.id, name=name.text)
        else:
            return await message.reply("**Wrong Input! Start Again By Hitting /update**")
        link = await client.ask(message.chat.id, "<b>Now Send Me Your Telegram Channel Link.\n\nSend Like This <code>https://t.me/CODExMOMO</code> ✅\n\nDo Not Send Like This @CODExMOMO ❌</b>")
        if link.text and link.text.startswith(('http://', 'https://')):
            await db.set_link(message.from_user.id, link=link.text)
        else:
            return await message.reply("**Wrong Input! Start Again By Hitting /update**")
        return await message.reply("<b>Updated Successfully ✅</b>")

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    fileid = file.file_id
    user_id = message.from_user.id
    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
    params = {'u': user_id, 'w': str(log_msg.id), 's': str(0), 't': str(0)}
    url1 = f"{urlencode(params)}"
    link = await encode(url1)
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(text=f"<code>{encoded_url}</code>", reply_markup=rm)

@Client.on_message(filters.private & filters.command("quality"))
async def quality_link(client, message):
    first_id = str(0)
    second_id = str(0)
    third_id = str(0)
    first = await client.ask(message.from_user.id, "<b>Send Me The Quality Of Your File.\n\n1. 480p or below → send <code>480</code>\n2. Above 480p upto 720p → send <code>720</code>\n3. Above 720p → send <code>1080</code></b>")
    if first.text == "480":
        f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
        if f_id.video or f_id.document:
            file = getattr(f_id, f_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            first_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    elif first.text == "720":
        s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
        if s_id.video or s_id.document:
            file = getattr(s_id, s_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            second_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    elif first.text == "1080":
        t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
        if t_id.video or t_id.document:
            file = getattr(t_id, t_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            third_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    else:
        return await message.reply("Choose From 480, 720 or 1080 Only. Send /quality Again To Start.")

    second = await client.ask(message.from_user.id, "<b>Send Me Another Quality.\n\n1. 480p or below → send <code>480</code>\n2. Above 480p upto 720p → send <code>720</code>\n3. Above 720p → send <code>1080</code>\n\nNote: Don't Use Same Quality Twice.</b>")
    if second.text != first.text and second.text == "480":
        f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
        if f_id.video or f_id.document:
            file = getattr(f_id, f_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            first_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    elif second.text != first.text and second.text == "720":
        s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
        if s_id.video or s_id.document:
            file = getattr(s_id, s_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            second_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    elif second.text != first.text and second.text == "1080":
        t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
        if t_id.video or t_id.document:
            file = getattr(t_id, t_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            third_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    else:
        return await message.reply("Choose From 480, 720 or 1080 Only. Send /quality Again To Start.")

    third = await client.ask(message.from_user.id, "<b>Send Me The Last Quality.\n\n1. 480p or below → send <code>480</code>\n2. Above 480p upto 720p → send <code>720</code>\n3. Above 720p → send <code>1080</code>\n\nNote: Don't Use Same Quality Twice.\n\nIf You Want Only 2 Quality Options Then Use <code>/getlink</code>.</b>")
    if third.text != second.text and third.text != first.text and third.text == "480":
        f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
        if f_id.video or f_id.document:
            file = getattr(f_id, f_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            first_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    elif third.text != second.text and third.text != first.text and third.text == "720":
        s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
        if s_id.video or s_id.document:
            file = getattr(s_id, s_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            second_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    elif third.text != second.text and third.text != first.text and third.text == "1080":
        t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
        if t_id.video or t_id.document:
            file = getattr(t_id, t_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            third_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input! Start Again By /quality")
    elif third.text == "/getlink":
        params = {'u': message.from_user.id, 'w': first_id, 's': second_id, 't': third_id}
        url1 = f"{urlencode(params)}"
        link = await encode(url1)
        encoded_url = f"{LINK_URL}?Tech_VJ={link}"
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
        return await message.reply_text(text=f"<code>{encoded_url}</code>", reply_markup=rm)
    else:
        return await message.reply("Choose From 480, 720 or 1080 Only. Send /quality Again To Start.")

    params = {'u': message.from_user.id, 'w': first_id, 's': second_id, 't': third_id}
    url1 = f"{urlencode(params)}"
    link = await encode(url1)
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(text=f"<code>{encoded_url}</code>", reply_markup=rm)

@Client.on_message(filters.private & filters.text & ~filters.command(["account", "withdraw", "notify", "quality", "start", "update"]))
async def link_start(client, message):
    if not message.text.startswith(LINK_URL):
        return
    link_part = message.text[len(LINK_URL + "?Tech_VJ="):].strip()
    try:
        original = await decode(link_part)
    except:
        return await message.reply("**Invalid Link!**")
    try:
        u, user_id, id, sec, th = original.split("=")
    except:
        return await message.reply("**Invalid Link!**")
    user_id = user_id.replace("&w", "")
    if user_id == message.from_user.id:
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=message.text)]])
        return await message.reply_text(text=f"<code>{message.text}</code>", reply_markup=rm)
    id = id.replace("&s", "")
    sec = sec.replace("&t", "")
    params = {'u': message.from_user.id, 'w': str(id), 's': str(sec), 't': str(th)}
    url1 = f"{urlencode(params)}"
    link = await encode(url1)
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(text=f"<code>{encoded_url}</code>", reply_markup=rm)

@Client.on_message(filters.private & filters.command("account"))
async def show_account(client, message):
    link_clicks = get_count(message.from_user.id)
    if link_clicks:
        balance = link_clicks / 1000.0
        formatted_balance = f"{balance:.2f}"
        response = f"<b>Your API Key :- <code>{message.from_user.id}</code>\n\nVideo Plays :- {link_clicks} (May Have Delay)\n\nBalance :- ${formatted_balance}</b>"
    else:
        response = f"<b>Your API Key :- <code>{message.from_user.id}</code>\nVideo Plays :- 0 (May Have Delay)\nBalance :- $0</b>"
    await message.reply(response)

@Client.on_message(filters.private & filters.command("withdraw"))
async def show_withdraw(client, message):
    w = get_withdraw(message.from_user.id)
    if w == True:
        return await message.reply("A Withdrawal Is Already In Process. Please Wait For It To Complete.")
    link_clicks = get_count(message.from_user.id)
    if not link_clicks:
        return await message.reply("**You Are Not Eligible For Withdrawal.\nMinimum 1000 Video Plays Required.**")
    if link_clicks >= 1000:
        confirm = await client.ask(message.from_user.id, "You Are About To Withdraw All Your Earnings. Are You Sure?\nSend /yes or /no")
        if confirm.text == "/no":
            return await message.reply("**Withdrawal Cancelled ❌**")
        else:
            pay = await client.ask(message.from_user.id, "Choose Your Payment Method:\n\n/upi - UPI, Webmoney, Airtm, Capitalist\n\n/bank - Bank Transfer Only")
            if pay.text == "/upi":
                upi = await client.ask(message.from_user.id, "Send Your UPI ID Or UPI Number With Your Name. Make Sure Name Matches Your UPI Account.")
                if not upi.text:
                    return await message.reply("**Wrong Input ❌**")
                upi = f"UPI - {pay.text}"
                try:
                    upi.delete()
                except:
                    pass
            else:
                name = await client.ask(message.from_user.id, "Send Your Account Holder Full Name.")
                if not name.text:
                    return await message.reply("**Wrong Input ❌**")
                number = await client.ask(message.from_user.id, "Send Your Account Number.")
                if not int(number.text):
                    return await message.reply("**Wrong Input ❌**")
                ifsc = await client.ask(message.from_user.id, "Send Your IFSC Code.")
                if not ifsc.text:
                    return await message.reply("**Wrong Input ❌**")
                bank_name = await client.ask(message.from_user.id, "Send Your Bank Name And Any Additional Contact Details.")
                if not bank_name.text:
                    return await message.reply("**Wrong Input ❌**")
                upi = f"Account Holder Name - {name.text}\n\nAccount Number - {number.text}\n\nIFSC Code - {ifsc.text}\n\nBank Name - {bank_name.text}\n\n"
                try:
                    name.delete()
                    number.delete()
                    ifsc.delete()
                    bank_name.delete()
                except:
                    pass
            traffic = await client.ask(message.from_user.id, "Send Your Traffic Source Link. If Clicks Are Fake, Payment Will Be Cancelled.")
            if not traffic.text:
                return await message.reply("**Invalid Traffic Source ❌**")
            balance = link_clicks / 1000.0
            formatted_balance = f"{balance:.2f}"
            text = f"API Key - {message.from_user.id}\n\n"
            text += f"Video Plays - {link_clicks}\n\n"
            text += f"Balance - ${formatted_balance}\n\n"
            text += upi
            text += f"Traffic Link - {traffic.text}"
            await client.send_message(ADMIN, text)
            record_withdraw(message.from_user.id, True)
            await message.reply(f"Your Withdrawal Balance - ${formatted_balance}\n\nWithdrawal Request Sent To Admin. If Everything Is Valid, Payment Will Be Made Within 3 Working Days.")
    else:
        await message.reply("Your Video Plays Are Less Than 1000. Minimum Payout Is 1000 Video Plays.")

@Client.on_message(filters.private & filters.command("notify") & filters.chat(ADMIN))
async def show_notify(client, message):
    count = int(1)
    user_id = await client.ask(message.from_user.id, "Send Me The API Key Of The User.")
    if int(user_id.text):
        sub = await client.ask(message.from_user.id, "Payment Cancelled Or Sent Successfully? /send or /cancel")
        if sub.text == "/send":
            record_visit(user_id.text, count)
            record_withdraw(user_id.text, False)
            await client.send_message(user_id.text, "Your Withdrawal Has Been Completed Successfully And Sent To Your Account.")
        else:
            reason = await client.ask(message.from_user.id, "Send The Reason For Payment Cancellation.")
            if reason.text:
                record_visit(user_id.text, count)
                record_withdraw(user_id.text, False)
                await client.send_message(user_id.text, f"Your Payment Was Cancelled - {reason.text}")
    await message.reply("Message Sent Successfully ✅")
