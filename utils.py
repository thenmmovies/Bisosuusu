import httpx
from pyrogram import Client, types
from configs import Config


async def send_post_views_request(bot: Client, link: str, quantity: int = Config.Defaults.QUANTITY):
    api_url = "https://n1panel.com/api/v2"
    payload = dict(
        key=Config.SMM_PANEL_API_KEY,
        action="add",
        service=2598,
        link=link,
        quantity=quantity
    )
    async with httpx.AsyncClient() as session:
        res = await session.post(api_url, data=payload)
        await bot.send_message(
            chat_id=Config.DUMP_CHANNEL_ID,
            text=f"Requested for @{link.rsplit('/', 2)[-2]}\n\n"
                 f"Quantity :{quantity}\n\n"
                 f"Channel Id : `{channel_id}`\n\n
                 f"OrderID: `{res.json().get('order', 0)}`\n\n"
                 "Post Link 👇",
            disable_web_page_preview=True,
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("Post Link", url=link)]]
            )
        )
