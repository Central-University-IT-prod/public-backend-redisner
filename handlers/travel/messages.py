from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

import assistive.callback as cb
from assistive.processors import location_to_text, country_to_text, city_to_text, travel_to_message
from assistive.states import UserTravelForm, IdleUser, EditingTravel
from database.functions import get_travels, create_travel_with_locations, update_data
from database.models import Travel
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.message(StateFilter(UserTravelForm.country), F.location)
async def request_location(message: Message, state: FSMContext):
    process_result = await location_to_text(message.location)

    current_data = await state.get_data()

    await message.answer(process_result["text"],
                         reply_markup=ReplyKeyboardRemove())

    if process_result["success"]:
        location = {
            "country": process_result["country"],
            "city": process_result["city"],
            "longitude": str(message.location.longitude),
            "latitude": str(message.location.latitude)
        }

        if "end_location" not in current_data:
            await state.update_data(end_location=location)

            await message.answer(f"<b>{_("request_start_location")}</b>",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text=_("fill_from_profile_button"),
                                                              callback_data=cb.LocationFromProfile().pack())
                                     ],
                                     [
                                         keyboards.cancel_button
                                     ]
                                 ]))
        else:
            await state.update_data(start_location=location)

            await state.set_state(UserTravelForm.start_date)

            await message.answer(f"<b>{_("request_start_date")}</b>",
                                 reply_markup=keyboards.cancel_action)

    elif process_result["city"] is None:
        if "end_location" not in current_data:
            await state.update_data(end_location={
                "country": process_result["country"]
            })
        else:
            await state.update_data(start_location={
                "country": process_result["country"]
            })

        await state.set_state(UserTravelForm.city)


@router.message(StateFilter(UserTravelForm.country), F.text)
async def request_country(message: Message, state: FSMContext):
    process_result = await country_to_text(message.text.capitalize())

    country = process_result["country"]

    location = {
        "country": country["name"]
    }

    current_data = await state.get_data()

    if process_result["success"]:
        if "end_location" in current_data and "city" in current_data["end_location"]:
            await state.update_data(start_location=location)
        else:
            await state.update_data(end_location=location)

        await state.set_state(UserTravelForm.city)

        final_text = (f"{process_result["text"]}\n"
                      f"\n"
                      f"{_("request_city")}")
    else:
        final_text = process_result["text"]

    await message.answer(final_text,
                         reply_markup=keyboards.cancel_action)


@router.message(StateFilter(UserTravelForm.city), F.text)
async def request_city(message: Message, state: FSMContext):
    current_data = await state.get_data()

    if "start_location" in current_data and "country" in current_data["start_location"]:
        country = current_data["start_location"]["country"]
    else:
        country = current_data["end_location"]["country"]

    process_result = await city_to_text(country,
                                        message.text.capitalize())

    city = process_result["city"]

    keyboard = keyboards.cancel_action

    if process_result["success"]:
        location = {"city": city["name"],
                    "country": country,
                    "longitude": city["longitude"],
                    "latitude": city["latitude"]}

        if "start_location" in current_data and "country" in current_data["start_location"]:
            await state.update_data(start_location=location)

            await state.set_state(UserTravelForm.start_date)

            final_text = (f"{process_result["text"]}\n"
                          f"\n"
                          f"{_("request_start_date")}")
        else:
            await state.update_data(end_location=location)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=_("fill_from_profile_button"),
                                         callback_data=cb.LocationFromProfile().pack())
                ],
                [
                    keyboards.cancel_button
                ]
            ])

            final_text = f"<b>{_("request_start_location")}</b>"

            await state.set_state(UserTravelForm.country)

    else:
        final_text = process_result["text"]

    await message.answer(final_text,
                         reply_markup=keyboard)


@router.message(StateFilter(UserTravelForm.start_date), F.text)
async def request_start_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, '%d.%m.%Y').date()

        await state.update_data(start_date=message.text)

        await state.set_state(UserTravelForm.end_date)

        await message.answer(f"<b>{_("request_end_date")}</b>",
                             reply_markup=keyboards.cancel_action)
    except:
        await message.delete()


@router.message(StateFilter(UserTravelForm.end_date), F.text)
async def request_end_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, '%d.%m.%Y').date()

        await state.update_data(end_date=message.text)

        await state.set_state(UserTravelForm.name)

        await message.answer(f"<b>{_("request_name")}</b>",
                             reply_markup=keyboards.cancel_action)
    except:
        await message.delete()


@router.message(StateFilter(UserTravelForm.name), F.text)
async def request_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(f"<b>{_("request_description")}</b>",
                         reply_markup=keyboards.skip_or_cancel)

    await state.set_state(UserTravelForm.description)


@router.message(StateFilter(UserTravelForm.description), F.text)
async def request_description(message: Message, state: FSMContext):
    travel_info = await state.get_data()

    new_travel_id = await create_travel_with_locations(creator_id=message.from_user.id,
                                                       travel_name=travel_info["name"],
                                                       description=message.text,
                                                       locations=[travel_info["start_location"],
                                                                  travel_info["end_location"]],
                                                       start_date=travel_info["start_date"],
                                                       end_date=travel_info["end_date"])

    travel = (await get_travels(message.from_user.id,
                                new_travel_id))[0]

    process_result = await travel_to_message(travel,
                                             message.from_user.id,
                                             message.bot)

    await message.answer(process_result["text"],
                         reply_markup=process_result["reply_markup"])

    await state.clear()

    await state.set_state(IdleUser.idle)


@router.message(StateFilter(EditingTravel.in_progress), F.text)
async def edit_user_info(message: Message, state: FSMContext):
    to_edit = await state.get_data()

    param = to_edit["param"]

    await update_data(Travel,
                      condition=(Travel.id == to_edit["travel_id"]),
                      update_values={param: message.text})

    await message.answer(f"<b>{_("successfully_saved")}</b>",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [
                                 InlineKeyboardButton(text=_("go_to_travel"),
                                                      callback_data=cb.Travel(travel_id=to_edit["travel_id"]).pack())
                             ]
                         ]))

    await state.clear()

    await state.set_state(IdleUser.idle)
