from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import assistive.callback as cb
from assistive.processors import user_info_to_text, add_participant_with_notify
from assistive.states import UserInfoForm, IdleUser, EditingUserInfo
from database.functions import add_data, get_data, find_matching_users
from database.models import User
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.callback_query(StateFilter(UserInfoForm.age), cb.Skip.filter())
async def skip_age(query: CallbackQuery, state: FSMContext):
    await state.update_data(age=None)

    await query.message.edit_text(f"<b>{_("request_interests")}</b>\n"
                                  f"\n"
                                  f"{_("command_to_skip")}",
                                  reply_markup=keyboards.skip_step)

    await state.set_state(UserInfoForm.interests)

    await query.answer()


@router.callback_query(StateFilter(UserInfoForm.bio), cb.Skip.filter())
async def skip_bio(query: CallbackQuery, state: FSMContext):
    await state.update_data(bio=None)

    final_info = await state.get_data()

    await add_data(User, check_condition=(User.id == query.from_user.id),
                   id=query.from_user.id,
                   country=final_info["country"], city=final_info["city"],
                   age=final_info["age"], bio=final_info["bio"],
                   longitude=final_info["longitude"], latitude=final_info["latitude"],
                   interests=final_info["interests"], gender=final_info["gender"])

    final_message = await user_info_to_text(final_info, query.from_user)

    await query.message.edit_text(final_message,
                                  reply_markup=keyboards.my_info)

    await state.clear()

    await state.set_state(IdleUser.idle)

    if final_info["invited_to"] is not None:
        await add_participant_with_notify(query.from_user,
                                          final_info["invited_to"],
                                          final_info["travel_name"],
                                          final_info["participants"],
                                          query.bot)

    await query.answer()


@router.callback_query(StateFilter(UserInfoForm.interests), cb.Skip.filter())
async def skip_interests(query: CallbackQuery, state: FSMContext):
    await state.update_data(interests=None)

    await query.message.edit_text(f"<b>{_("request_gender")}</b>",
                                  reply_markup=keyboards.gender)

    await state.set_state(UserInfoForm.gender)

    await query.answer()


@router.callback_query(StateFilter(UserInfoForm.gender), cb.Skip.filter())
async def skip_gender(query: CallbackQuery, state: FSMContext):
    await state.update_data(gender=None)

    await query.message.edit_text(f"<b>{_("request_bio")}</b>\n"
                                  f"\n"
                                  f"{_("command_to_skip")}",
                                  reply_markup=keyboards.skip_step)

    await state.set_state(UserInfoForm.bio)

    await query.answer()


@router.callback_query(StateFilter(UserInfoForm.gender), cb.Gender.filter())
async def request_gender(query: CallbackQuery, state: FSMContext, callback_data: cb.Gender):
    await state.update_data(gender=callback_data.gender)

    await query.message.edit_text(f"<b>{_("request_bio")}</b>\n"
                                  f"\n"
                                  f"{_("command_to_skip")}",
                                  reply_markup=keyboards.skip_step)

    await state.set_state(UserInfoForm.bio)

    await query.answer()


@router.callback_query(cb.FindTravelers.filter())
async def find_travelers(query: CallbackQuery):
    matching_users = await find_matching_users(query.from_user.id)

    message_elements = [f"<b>{_("matching_users")}</b>",
                        ""]

    if not matching_users:
        message_elements += [f"{_("there_is_no_users")}"]

    for user in matching_users:
        user_info = {
            "country": user.country,
            "city": user.city,
            "age": user.age,
            "gender": user.city,
            "interests": user.interests,
            "bio": user.bio
        }

        user_text = await user_info_to_text(user_info,
                                            await query.bot.get_chat(user.id),
                                            matching=True)

        message_elements += [f"{user_text}",
                             ""]

    await query.message.edit_text("\n".join(message_elements),
                                  reply_markup=keyboards.back_to_menu)

    await query.answer()


@router.callback_query(cb.MyInfo.filter())
async def my_info_menu(query: CallbackQuery):
    user_info = (await get_data(User,
                                condition=User.id == query.from_user.id)).first()

    final_message = await user_info_to_text({
        "country": user_info.country,
        "city": user_info.city,
        "age": user_info.age,
        "bio": user_info.bio,
        "gender": user_info.gender,
        "interests": user_info.interests
    },
        query.from_user)

    await query.message.edit_text(final_message,
                                  reply_markup=keyboards.my_info)

    await query.answer()


@router.callback_query(cb.EditInfoPage.filter())
async def edit_info_menu(query: CallbackQuery):
    await query.message.edit_reply_markup(reply_markup=keyboards.edit_info)

    await query.answer()


@router.callback_query(cb.EditInfo.filter())
async def edit_any_info(query: CallbackQuery,
                        callback_data: cb.EditInfo,
                        state: FSMContext):
    to_edit = callback_data.param

    if to_edit == "location":
        input_new = _("input_new_location")

        keyboard = keyboards.request_location

        await state.set_state(UserInfoForm.country)

        await state.update_data(editing=True)
    else:
        input_new = _("input_new")

        keyboard = None

        await state.set_state(EditingUserInfo.in_progress)

        await state.update_data(param=to_edit)

    await query.message.answer(f"<b>{_("editing")}: {_(to_edit)}</b>",
                               reply_markup=keyboard)

    await query.message.answer(f"<b>{input_new}</b>",
                               reply_markup=keyboards.cancel_action)

    await query.answer()
