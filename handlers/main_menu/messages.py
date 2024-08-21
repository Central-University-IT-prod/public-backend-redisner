from aiogram import Router
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

import assistive.callback as cb
from assistive.processors import add_participant_with_notify
from assistive.states import IdleUser
from database.functions import get_travels
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.message(StateFilter(IdleUser.idle), Command("start"))
async def start_menu(message: Message,
                     command: CommandObject):
    arg = command.args

    try:
        if "_" in arg and len(arg.split("_")) == 2:
            inviter_id, travel_id = arg.split("_")

            travel = await get_travels(int(inviter_id),
                                       travel_id)

            if travel:
                travel = travel[0]

                travel_name = travel["name"]

                user_id = message.from_user.id

                participants_ids = [x["user_id"] for x in travel["participants"]]

                if user_id not in participants_ids:
                    await message.answer(f"<b>{_("invite_to")} «{travel_name}» {_("accepted")}</b>",
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                             [
                                                 InlineKeyboardButton(text=_("go_to_travel"),
                                                                      callback_data=cb.Travel(
                                                                          travel_id=travel_id).pack())
                                             ]
                                         ]))

                    await add_participant_with_notify(message.from_user,
                                                      travel_id,
                                                      travel_name,
                                                      participants_ids,
                                                      message.bot)

                    return

        await message.answer(f"<b>{_("menu_text")}</b>",
                             reply_markup=keyboards.main_menu)
    except:
        await message.answer(f"<b>{_("menu_text")}</b>",
                             reply_markup=keyboards.main_menu)
