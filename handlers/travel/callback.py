from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile

from assistive import callback as cb
from assistive.processors import travel_to_message
from assistive.states import UserTravelForm, EditingTravel, IdleUser
from database.functions import get_travels, create_travel_with_locations, get_data, delete_data
from database.models import User, Travel
from external.openstreetmap import plot_route
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.callback_query(cb.MyTravels.filter())
async def my_travels_menu(query: CallbackQuery):
    travels = await get_travels(query.from_user.id)

    message_elements = [f"<b>{_("your_travels")}</b>"]

    if not travels:
        message_elements += ["",
                             _("there_is_nothing_here_yet")]

    buttons = []

    for travel in travels:
        buttons += [
            [
                InlineKeyboardButton(text=travel["name"],
                                     callback_data=cb.Travel(travel_id=travel["id"]).pack()),
            ]
        ]

    final_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons + keyboards.travel_buttons)

    await query.message.edit_text("\n".join(message_elements),
                                  reply_markup=final_keyboard)

    await query.answer()


@router.callback_query(cb.NewTravel.filter())
async def new_travel_menu(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(f"<b>{_("new_travel_header")}</b>\n"
                                  f"\n"
                                  f"{_("request_location")}",
                                  reply_markup=keyboards.cancel_action)

    await state.set_state(UserTravelForm.country)

    await query.answer()


@router.callback_query(cb.Travel.filter())
async def travel_page(query: CallbackQuery, callback_data: cb.Travel):
    travel_id = callback_data.travel_id

    travel = (await get_travels(user_id=query.from_user.id,
                                travel_id=travel_id))[0]

    process_result = await travel_to_message(travel,
                                             query.from_user.id,
                                             query.bot)

    await query.message.answer(process_result["text"],
                               reply_markup=process_result["reply_markup"])

    await query.message.delete()

    await query.answer()


@router.callback_query(cb.EditTravelPage.filter())
async def edit_travel_page(query: CallbackQuery, callback_data: cb.EditTravelPage):
    travel_id = callback_data.travel_id

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("edit_travel_name_button"),
                                 callback_data=cb.EditTravel(travel_id=travel_id,
                                                             param="name").pack())
        ],
        [
            InlineKeyboardButton(text=_("edit_travel_description_button"),
                                 callback_data=cb.EditTravel(travel_id=travel_id,
                                                             param="description").pack())
        ],
        [
            InlineKeyboardButton(text=_("back_button"),
                                 callback_data=cb.Travel(travel_id=travel_id).pack())
        ]
    ])

    await query.message.edit_reply_markup(reply_markup=keyboard)

    await query.answer()


@router.callback_query(cb.EditTravel.filter())
async def edit_travel_props(query: CallbackQuery,
                            callback_data: cb.EditTravel,
                            state: FSMContext):
    to_edit = callback_data.param

    await state.set_state(EditingTravel.in_progress)

    await state.update_data(param=to_edit,
                            travel_id=callback_data.travel_id)

    await query.message.edit_text(f"<b>{_("editing")}: {_(to_edit)}</b>\n"
                                  f"\n"
                                  f"<b>{_("input_new")}</b>",
                                  reply_markup=keyboards.cancel_action)

    await query.answer()


@router.callback_query(StateFilter(UserTravelForm.description), cb.Skip.filter())
async def skip_description(query: CallbackQuery, state: FSMContext):
    travel_info = await state.get_data()

    new_travel_id = await create_travel_with_locations(creator_id=query.from_user.id,
                                                       travel_name=travel_info["name"],
                                                       description=None,
                                                       locations=[travel_info["start_location"],
                                                                  travel_info["end_location"]])

    travel = (await get_travels(query.from_user.id,
                                new_travel_id))[0]

    process_result = await travel_to_message(travel,
                                             query.from_user.id,
                                             query.bot)

    await query.message.edit_text(process_result["text"],
                                  reply_markup=process_result["reply_markup"])

    await state.clear()

    await state.set_state(IdleUser.idle)

    await query.answer()


@router.callback_query(cb.TravelRoute.filter())
async def route_callback(query: CallbackQuery, callback_data: cb.TravelRoute):
    travel_id = callback_data.travel_id

    travel = (await get_travels(query.from_user.id,
                                travel_id))[0]

    user = (await get_data(User, User.id == query.from_user.id)).first()

    locations = [{
        "latitude": user.latitude,
        "longitude": user.longitude
    }] + travel["locations"]

    locations = [(float(location["latitude"]), float(location["longitude"])) for location in locations]

    route = await plot_route(locations)

    await query.message.answer_photo(BufferedInputFile(route, filename="route.png"),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [
                                             InlineKeyboardButton(text=_("back_button"),
                                                                  callback_data=cb.Travel(travel_id=travel_id).pack())
                                         ]
                                     ]
                                     ))

    await query.message.delete()

    await query.answer()


@router.callback_query(cb.LocationFromProfile.filter(), StateFilter(UserTravelForm.country))
async def location_from_profile(query: CallbackQuery,
                                state: FSMContext):
    user = (await get_data(User, User.id == query.from_user.id)).first()

    location = {
        "country": user.country,
        "city": user.city,
        "longitude": str(user.longitude),
        "latitude": str(user.latitude)
    }

    await state.update_data(start_location=location)

    await state.set_state(UserTravelForm.start_date)

    await query.message.edit_text(f"<b>{_("request_start_date")}</b>",
                                  reply_markup=keyboards.cancel_action)

    await query.answer()


@router.callback_query(cb.DeleteTravel.filter())
async def delete_callback(query: CallbackQuery, callback_data: cb.DeleteTravel):
    travel_id = callback_data.travel_id

    await delete_data(Travel, Travel.id == travel_id)

    await query.message.edit_text(f"<b>{_("travel_deleted")}</b>",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboards.back_to_my_travels]))

    await query.answer()
