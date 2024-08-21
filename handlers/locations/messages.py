from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

import assistive.callback as cb
from assistive.processors import location_to_text, country_to_text, city_to_text, location_to_message
from assistive.states import IdleUser, LocationEditing, CreateLocationForm
from database.functions import get_travels, update_data, add_data
from database.models import Location
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.message(StateFilter(LocationEditing.date), F.text)
async def edit_location_date_msg(message: Message,
                                 state: FSMContext):
    try:
        date = datetime.strptime(message.text, '%d.%m.%Y').date()

        current_data = await state.get_data()

        await update_data(Location, Location.id == current_data["location_id"],
                          {f"{current_data["date_type"]}_date": date})

        await state.set_state(IdleUser.idle)

        await message.answer(f"<b>{_("successfully_edited")}</b>",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     InlineKeyboardButton(text=_("back_button"),
                                                          callback_data=cb.EditLocation(
                                                              location_id=current_data["location_id"],
                                                              travel_id=current_data["travel_id"]).pack())
                                 ]
                             ]))
    except:
        await message.delete()


@router.message(StateFilter(CreateLocationForm.country), F.location)
async def request_location(message: Message, state: FSMContext):
    process_result = await location_to_text(message.location)

    await state.update_data(country=process_result["country"],
                            city=process_result["city"],
                            longitude=str(message.location.longitude),
                            latitude=str(message.location.longitude))

    if process_result["success"]:
        await state.set_state(CreateLocationForm.start_date)
    elif process_result["city"] is None:
        await state.set_state(CreateLocationForm.city)

    await message.answer(process_result["text"],
                         reply_markup=ReplyKeyboardRemove())

    if process_result["success"]:
        await message.answer(f"<b>{_("request_start_date")}</b>",
                             reply_markup=keyboards.cancel_action)


@router.message(StateFilter(CreateLocationForm.country), F.text)
async def request_country(message: Message, state: FSMContext):
    process_result = await country_to_text(message.text.capitalize())

    country = process_result["country"]

    if process_result["success"]:
        await state.update_data(country=country["name"])

        await state.set_state(CreateLocationForm.city)

        final_text = (f"{process_result["text"]}\n"
                      f"\n"
                      f"{_("request_city")}")
    else:
        final_text = process_result["text"]

    await message.answer(final_text,
                         reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(CreateLocationForm.city), F.text)
async def request_city(message: Message, state: FSMContext):
    country = (await state.get_data())["country"]

    process_result = await city_to_text(country,
                                        message.text.capitalize())

    city = process_result["city"]

    if process_result["success"]:
        await state.update_data(city=city["name"],
                                longitude=city["longitude"],
                                latitude=city["latitude"])

        await state.set_state(CreateLocationForm.start_date)

    await message.answer(process_result["text"],
                         reply_markup=ReplyKeyboardRemove())

    if process_result["success"]:
        await message.answer(f"<b>{_("request_start_date")}</b>",
                             reply_markup=keyboards.cancel_action)


@router.message(StateFilter(CreateLocationForm.start_date), F.text)
async def request_start_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, '%d.%m.%Y').date()

        await state.update_data(start_date=message.text)

        await state.set_state(CreateLocationForm.end_date)

        await message.answer(f"<b>{_("request_end_date")}</b>",
                             reply_markup=keyboards.cancel_action)
    except:
        await message.delete()


@router.message(StateFilter(CreateLocationForm.end_date), F.text)
async def request_end_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, '%d.%m.%Y').date()

        await state.update_data(end_date=message.text)

        final_info = await state.get_data()

        travel_id = final_info["travel_id"]

        final_info["start_date"] = datetime.strptime(final_info["start_date"], '%d.%m.%Y').date()
        final_info["end_date"] = datetime.strptime(final_info["end_date"], '%d.%m.%Y').date()

        location: Location = await add_data(Location, False, None, **final_info)

        travel: dict = (await get_travels(message.from_user.id, travel_id))[0]

        process_result = await location_to_message(location,
                                                   travel,
                                                   message.from_user.id,
                                                   "edit")

        await message.answer(process_result["text"],
                             reply_markup=process_result["reply_markup"])

        await state.clear()

        await state.set_state(IdleUser.idle)
    except Exception as e:
        await message.answer(str(e))
        await message.delete()
