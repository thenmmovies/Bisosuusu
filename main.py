# (c) @AbirHasan2005

import asyncio
import logging
import pyromod.listen
from database import db
from configs import Config
from humanfriendly import format_timespan
from utils import send_post_views_request
from pyrogram import Client, filters, types

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)
bot = Client(
    name="pyrogram",
    in_memory=True,
    api_id=Config.TG_API_ID,
    api_hash=Config.TG_API_HASH,
    bot_token=Config.TG_BOT_TOKEN
)


@bot.on_message(filters=filters.command("start") & filters.private)
async def start_cmd_handler(_, m: "types.Message"):
    return await m.reply_text(
        "Hi, I'm Alive Brother\n\nContact @Nmfajis For Purcahsing Views Plan .",
        quote=True,
        disable_web_page_preview=True,
        reply_markup=types.InlineKeyboardMarkup(
            [
                [types.InlineKeyboardButton("Contact Now", url="https://t.me/NmFajis")]
            ]
        )
    )


@bot.on_message(filters=(filters.text | filters.media) & filters.channel)
async def channel_msgs_handler(_, m: "types.Message"):
    if not await db.is_doc_exist(m.chat.id):
        return None
    await send_post_views_request(
        bot,
        link=m.link,
        quantity=await db.get_quantity(m.chat.id)
    )




@bot.on_message(filters=filters.command("settings") & filters.user(Config.ADMIN_IDS) & filters.private)
async def settings_cmd_handler(_, m: "types.Message"):
    sent_msg = await m.reply_text("Send me channel ID", True)
    try:
        user_msg: "types.Message" = await bot.listen(
            chat_id=m.chat.id,
            timeout=300  # wait in seconds for user to input
        )
    except asyncio.TimeoutError:
        return await sent_msg.edit("Timeout!")
    if not (user_msg.text and user_msg.text.startswith("-100")):
        return await sent_msg.edit("Not a valid Telegram channel ID !!")
    channel_id = int(user_msg.text)
    await m.reply_text(
        text=f"Here is setup panel of `{channel_id}`:\n\n"
             f"**Quantity:** `{await db.get_quantity(channel_id)} views`\n"
             f"**Time Gap:** `{format_timespan(await db.get_sleep_time(channel_id))}`",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [types.InlineKeyboardButton("Set Quantity", callback_data=f"setQuantity_{channel_id}"),
                 types.InlineKeyboardButton("Set Time Gap", callback_data=f"setTimeGap_{channel_id}")],
                [types.InlineKeyboardButton("Add Channel", callback_data="addChannel"),
                 types.InlineKeyboardButton("Remove Channel", callback_data="rmChannel")]
            ]
        ),
        quote=True
    )


@bot.on_callback_query()
async def cb_handlers(_, cb: "types.CallbackQuery"):
    if cb.data == "addChannel":
        sent_msg = await cb.message.reply_text("Send Telegram Channel ID to add:")
        try:
            user_msg: "types.Message" = await bot.listen(
                chat_id=cb.message.chat.id,
                timeout=300  # wait in seconds for user to input
            )
        except asyncio.TimeoutError:
            return await sent_msg.edit("Timeout!")
        if not (user_msg.text and user_msg.text.startswith("-100")):
            return await sent_msg.edit("Send me only number of quantity! Try again.")
        if await db.is_doc_exist(int(user_msg.text)):
            return await sent_msg.edit("This channel already exists in database !!")
        await db.add_doc(doc_id=int(user_msg.text))
        await sent_msg.edit(f"**ChannelID Added:** `{user_msg.text}`\n\n"
                            "Now setup channel settings from /settings")

    if cb.data == "rmChannel":
        sent_msg = await cb.message.reply_text("Send Telegram Channel ID to remove:")
        try:
            user_msg: "types.Message" = await bot.listen(
                chat_id=cb.message.chat.id,
                timeout=300  # wait in seconds for user to input
            )
        except asyncio.TimeoutError:
            return await sent_msg.edit("Timeout!")
        if not (user_msg.text and user_msg.text.startswith("-100")):
            return await sent_msg.edit("Send me only number of quantity! Try again.")
        if not await db.is_doc_exist(int(user_msg.text)):
            return await sent_msg.edit("This channel already not exists in database !!")
        await db.delete_doc(doc_id=int(user_msg.text))
        await sent_msg.edit(f"**ChannelID Removed:** `{user_msg.text}`")

    if cb.data.startswith("setQuantity"):
        channel_id = int(cb.data.split("_", 1)[-1])
        if not await db.is_doc_exist(channel_id):
            return await cb.answer("Channel Removed from Database !!", show_alert=True)
        sent_msg = await cb.message.reply_text("Send Quantity:")
        try:
            user_msg: "types.Message" = await bot.listen(
                chat_id=cb.message.chat.id,
                timeout=300  # wait in seconds for user to input
            )
        except asyncio.TimeoutError:
            return await sent_msg.edit("Timeout!")
        if not (user_msg.text and user_msg.text.isdigit()):
            return await sent_msg.edit("Send me only number of quantity! Try again.")
        await db.set_quantity(channel_id, quantity=int(user_msg.text))
        await sent_msg.edit(f"**Quantity:** `{await db.get_quantity(channel_id)}`")

    if cb.data.startswith("setTimeGap"):
        channel_id = int(cb.data.split("_", 1)[-1])
        if not await db.is_doc_exist(channel_id):
            return await cb.answer("Channel Removed from Database !!", show_alert=True)
        sent_msg = await cb.message.reply_text("Send Time Gap in minutes:")
        try:
            user_msg: "types.Message" = await bot.listen(
                chat_id=cb.message.chat.id,
                timeout=300  # wait in seconds for user to input
            )
        except asyncio.TimeoutError:
            return await sent_msg.edit("Timeout!")
        if not (user_msg.text and user_msg.text.isdigit()):
            return await sent_msg.edit("Send me only number of minutes! Try again.")
        await db.set_sleep_time(channel_id, sleep_time=int(user_msg.text) * 60)
        await sent_msg.edit(f"**Time Gap:** `{await db.get_sleep_time(channel_id) / 60} minutes`")


bot.run()
