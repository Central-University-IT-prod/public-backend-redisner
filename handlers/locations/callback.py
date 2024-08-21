from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from assistive import callback as cb
from assistive.processors import location_to_message
from assistive.states import LocationEditing, CreateLocationForm
from database.functions import get_travels, get_data, delete_data
from database.models import Location
from external.foursquare import search_places
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.callback_query(cb.TravelLocationsMenu.filter())
async def all_locations_menu(query: CallbackQuery,
                             callback_data: cb.TravelLocationsMenu):
    travel_id = callback_data.travel_id

    travel = (await get_travels(query.from_user.id, travel_id))[0]

    locations = travel["locations"]

    buttons = [
        [
            InlineKeyboardButton(text=_("add_location_button"),
                                 callback_data=cb.AddLocation(travel_id=travel_id).pack())
        ]
    ]

    buttons += [
        [
            InlineKeyboardButton(text=f"{location["city"]} ({location["start_date"].strftime("%d.%m.%Y")})",
                                 callback_data=cb.LocationPage(travel_id=travel_id,
                                                               location_id=location["id"]).pack())
        ] for location in locations
    ]

    buttons += [
        [
            InlineKeyboardButton(text=_("back_button"),
                                 callback_data=cb.Travel(travel_id=travel_id).pack())
        ]
    ]

    await query.message.edit_text(f"<b>{_("all_locations_in_travel")}</b>",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

    await query.answer()


@router.callback_query(cb.LocationPage.filter())
async def location_page(query: CallbackQuery,
                        callback_data: cb.LocationPage):
    travel_id = callback_data.travel_id
    location_id = callback_data.location_id

    travel: dict = (await get_travels(query.from_user.id, travel_id))[0]
    location: Location = (await get_data(Location, Location.id == location_id)).first()

    process_result = await location_to_message(location,
                                               travel,
                                               query.from_user.id,
                                               "page")

    await query.message.edit_text(process_result["text"],
                                  reply_markup=process_result["reply_markup"])

    await query.answer()


@router.callback_query(cb.EditLocation.filter())
async def edit_location(query: CallbackQuery,
                        callback_data: cb.EditLocation):
    travel_id = callback_data.travel_id
    location_id = callback_data.location_id

    travel: dict = (await get_travels(query.from_user.id, travel_id))[0]
    location: Location = (await get_data(Location, Location.id == location_id)).first()

    process_result = await location_to_message(location,
                                               travel,
                                               query.from_user.id,
                                               "edit")

    await query.message.edit_text(process_result["text"],
                                  reply_markup=process_result["reply_markup"])

    await query.answer()


@router.callback_query(cb.EditLocationDate.filter())
async def edit_location_date_callback(query: CallbackQuery,
                                      callback_data: cb.EditLocationDate,
                                      state: FSMContext):
    await state.update_data(location_id=callback_data.location_id,
                            date_type=callback_data.date_type,
                            travel_id=callback_data.travel_id)

    await state.set_state(LocationEditing.date)

    await query.message.edit_text(f"<b>{_("editing")}: {_(callback_data.date_type + "_date")}</b>\n"
                                  f"\n"
                                  f"{_("input_new")}",
                                  reply_markup=keyboards.cancel_action)

    await query.answer()


@router.callback_query(cb.AddLocation.filter())
async def add_location_callback(query: CallbackQuery,
                                callback_data: cb.AddLocation,
                                state: FSMContext):
    await state.set_state(CreateLocationForm.country)

    await state.update_data(travel_id=callback_data.travel_id)

    await query.message.edit_text(f"<b>{_("input_new_location")}</b>",
                                  reply_markup=keyboards.cancel_action)

    await query.answer()


@router.callback_query(cb.DeleteLocation.filter())
async def delete_location_callback(query: CallbackQuery,
                                   callback_data: cb.DeleteLocation):
    await delete_data(Location, Location.id == callback_data.location_id)

    await query.message.edit_text(f"<b>{_("location_deleted")}</b>",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text=_("back_button"),
                                                               callback_data=cb.TravelLocationsMenu(
                                                                   travel_id=callback_data.travel_id).pack())
                                      ]
                                  ]))

    await query.answer()


@router.callback_query(cb.LocationPlaces.filter())
async def location_places_callback(query: CallbackQuery,
                                   callback_data: cb.LocationPlaces):
    location_id = callback_data.location_id
    place_type = callback_data.place_type

    location: Location = (await get_data(Location, Location.id == location_id)).first()

    places = await search_places(location.latitude,
                                 location.longitude,
                                 place_type)

    message_elements = [f"<b>{_(f"location_places_{place_type}")}</b>"]

    for place in places:
        message_elements += ["",
                             f"{_(f"{place_type}_emoji")} {place["name"]}",
                             f"📍 {place["address"]}",
                             f"⭐ {place["rating"]}/10"]

        if place["description"] is not None:
            message_elements += [f"💬 {place["description"]}"]

    await query.message.edit_text("\n".join(message_elements),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text=_("back_button"),
                                                               callback_data=cb.LocationPage(
                                                                   travel_id=location.travel_id,
                                                                   location_id=location_id).pack())
                                      ]
                                  ]))

    await query.answer()
