import asyncio

from aiogram import Router, F
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from assistive.processors import user_info_to_text, location_to_text, country_to_text, city_to_text, \
    add_participant_with_notify
from assistive.states import UserInfoForm, IdleUser, EditingUserInfo
from database.functions import add_data, get_travels, update_data
from database.models import User
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.message(StateFilter(None), Command("start"))
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.update_data(id=message.from_user.id,
                            invited_to=None)

    arg = command.args

    try:
        if "_" in arg and len(arg.split("_")) == 2:
            inviter_id, travel_id = arg.split("_")

            travel = await get_travels(int(inviter_id),
                                       travel_id)

            if travel:
                travel = travel[0]

                participants = [x["user_id"] for x in travel["participants"]]

                if message.from_user.id not in participants:
                    await message.answer(f"<b>{_("invite_to")} «{travel["name"]}» {_("accepted")}</b>\n"
                                         f"\n"
                                         f"{_("reg_to_finish")}")

                    await state.update_data(invited_to=travel_id,
                                            participants=participants,
                                            travel_name=travel["name"])
    except:
        pass

    await message.answer(f"<b>{_("greeting")}, {message.from_user.first_name}! {_("my_name_is")}</b>\n"
                         f"{_("who_am_i")}\n"
                         f"\n"
                         f"<b>{_("what_i_can_do")}</b>\n"
                         f"\n"
                         f"{_("can_do_1")}\n"
                         f"{_("can_do_2")}\n"
                         f"{_("can_do_3")}\n"
                         f"\n"
                         f"{_("and_much_more")}")

    await asyncio.sleep(0.3)

    await message.answer(f"<b>{_("time_to_meet")}</b>\n"
                         f"\n"
                         f"{_("meet_explanation")}")

    await asyncio.sleep(0.3)

    await message.answer(f"{_("request_location")}",
                         reply_markup=keyboards.request_location)

    await state.set_state(UserInfoForm.country)


@router.message(StateFilter(UserInfoForm.country), F.location)
async def request_location(message: Message, state: FSMContext):
    process_result = await location_to_text(message.location)

    await state.update_data(country=process_result["country"],
                            city=process_result["city"],
                            longitude=str(message.location.longitude),
                            latitude=str(message.location.longitude))

    if process_result["success"]:
        await state.set_state(UserInfoForm.age)
    elif process_result["city"] is None:
        await state.set_state(UserInfoForm.city)

    await message.answer(process_result["text"],
                         reply_markup=ReplyKeyboardRemove())

    if process_result["success"]:
        if "editing" in await state.get_data():
            await update_data(User,
                              condition=(User.id == message.from_user.id),
                              update_values={"country": process_result["country"],
                                             "city": process_result["city"],
                                             "longitude": str(message.location.longitude),
                                             "latitude": str(message.location.latitude)})

            await message.answer(f"<b>{_("successfully_saved")}</b>",
                                 reply_markup=keyboards.after_info_edit)

            await state.clear()

            await state.set_state(IdleUser.idle)
        else:
            await message.answer(f"{_("request_age")}\n"
                                 f"\n"
                                 f"{_("command_to_skip")}",
                                 reply_markup=keyboards.skip_step)


@router.message(StateFilter(UserInfoForm.country), F.text)
async def request_country(message: Message, state: FSMContext):
    process_result = await country_to_text(message.text.capitalize())

    country = process_result["country"]

    if process_result["success"]:
        await state.update_data(country=country["name"])

        await state.set_state(UserInfoForm.city)

        final_text = (f"{process_result["text"]}\n"
                      f"\n"
                      f"{_("request_city")}")
    else:
        final_text = process_result["text"]

    await message.answer(final_text,
                         reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(UserInfoForm.city), F.text)
async def request_city(message: Message, state: FSMContext):
    country = (await state.get_data())["country"]

    process_result = await city_to_text(country,
                                        message.text.capitalize())

    city = process_result["city"]

    if process_result["success"]:
        await state.update_data(city=city["name"],
                                longitude=city["longitude"],
                                latitude=city["latitude"])

        await state.set_state(UserInfoForm.age)

    await message.answer(process_result["text"],
                         reply_markup=ReplyKeyboardRemove())

    if process_result["success"]:
        if "editing" in await state.get_data():
            await update_data(User,
                              condition=(User.id == message.from_user.id),
                              update_values={"country": country,
                                             "city": city["name"],
                                             "longitude": city["longitude"],
                                             "latitude": city["latitude"]})

            await message.answer(f"<b>{_("successfully_saved")}</b>",
                                 reply_markup=keyboards.after_info_edit)

            await state.clear()

            await state.set_state(IdleUser.idle)
        else:
            await message.answer(f"{_("request_age")}\n"
                                 f"\n"
                                 f"{_("command_to_skip")}",
                                 reply_markup=keyboards.skip_step)


@router.message(StateFilter(UserInfoForm.age), F.text)
async def request_age(message: Message, state: FSMContext):
    if any(not x.isdigit() for x in message.text):
        await message.answer(_("invalid_age"))
        return

    await state.update_data(age=int(message.text))

    await message.answer(f"<b>{_("request_interests")}</b>\n"
                         f"\n"
                         f"{_("command_to_skip")}",
                         reply_markup=keyboards.skip_step)

    await state.set_state(UserInfoForm.interests)


@router.message(StateFilter(UserInfoForm.interests), F.text)
async def request_interests(message: Message, state: FSMContext):
    interests = [x.strip() for x in message.text.lower().split(",")]

    await state.update_data(interests=interests)

    await message.answer(f"<b>{_("request_gender")}</b>",
                         reply_markup=keyboards.gender)

    await state.set_state(UserInfoForm.gender)


@router.message(StateFilter(UserInfoForm.bio), F.text)
async def request_bio(message: Message, state: FSMContext):
    user_id = message.from_user.id

    await state.update_data(bio=message.text)

    final_info = await state.get_data()

    await add_data(User, check_condition=(User.id == user_id),
                   id=user_id,
                   country=final_info["country"], city=final_info["city"],
                   age=final_info["age"], bio=final_info["bio"],
                   longitude=final_info["longitude"], latitude=final_info["latitude"],
                   interests=final_info["interests"], gender=final_info["gender"])

    final_message = await user_info_to_text(final_info, message.from_user)

    await message.answer(final_message,
                         reply_markup=keyboards.my_info)

    if final_info["invited_to"] is not None:
        await add_participant_with_notify(message.from_user,
                                          final_info["invited_to"],
                                          final_info["travel_name"],
                                          final_info["participants"],
                                          message.bot)

    await state.clear()

    await state.set_state(IdleUser.idle)


@router.message(StateFilter(EditingUserInfo.in_progress), F.text)
async def edit_user_info(message: Message, state: FSMContext):
    to_edit = await state.get_data()
    param = to_edit["param"]

    if param == "age":
        if any(not x.isdigit() for x in message.text):
            await message.answer(_("invalid_age"))
            return

        updated = int(message.text)
    elif param == "bio":
        updated = message.text
    elif param == "interests":
        updated = [x.strip() for x in message.text.lower().split(",")]

    await update_data(User,
                      condition=(User.id == message.from_user.id),
                      update_values={param: updated})

    await message.answer(f"<b>{_("successfully_saved")}</b>",
                         reply_markup=keyboards.after_info_edit)

    await state.set_state(IdleUser.idle)
