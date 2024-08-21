from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle, \
    InputTextMessageContent

from database.functions import get_travels
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.inline_query()
async def invitations_list(inline_query: InlineQuery):
    bot_username = (await inline_query.bot.get_me()).username

    offset = int(inline_query.offset) if inline_query.offset else 0

    user_id = inline_query.from_user.id
    travel_id = None

    if inline_query.query:
        travel_id = inline_query.query

    travels = await get_travels(user_id,
                                travel_id)

    results = []

    for travel in travels:
        description = travel["description"]
        desc_exists = description is not None

        locations_string = " -> ".join([x["city"] for x in travel["locations"]])

        results += [
            InlineQueryResultArticle(
                id=f"{user_id}_{travel["id"]}",
                title=f"{_("invite_to")} «{travel["name"]}»",
                description=f"{locations_string}" + (f" | {description}" if desc_exists else ""),
                input_message_content=InputTextMessageContent(
                    message_text=f"<b>{_("invite_to")} «{travel["name"]}»</b>"
                                 f"\n\n"
                                 f"📌 {locations_string}" +
                                 (f"\n\n"
                                  f"💬 {_("description")}: {description}" if desc_exists else "")
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text=_("accept_invite"),
                                             url=f"https://t.me/{bot_username}?start={user_id}_{travel["id"]}")
                    ]
                ])
            )
        ]

    if len(results) < 50:
        await inline_query.answer(
            results, is_personal=True
        )
    else:
        await inline_query.answer(
            results, is_personal=True,
            next_offset=str(offset + 50)
        )
