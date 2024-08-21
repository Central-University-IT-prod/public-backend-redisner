from typing import List

import aiogram.types
from aiogram import Bot
from aiogram.types import User, InlineKeyboardMarkup, InlineKeyboardButton, SwitchInlineQueryChosenChat

import assistive.callback as cb
import external.openstreetmap as osm
from database.functions import add_data
from database.models import UserTravel, Location
from external.openweathermap import get_weather
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get


async def user_info_to_text(final_info: dict,
                            user: aiogram.types.User | aiogram.types.Chat,
                            matching=False) -> str:
    country, city, age, bio, gender, interests = final_info["country"], final_info["city"], final_info["age"], \
        final_info["bio"], final_info["gender"], final_info["interests"]

    message_elements = []

    if not matching:
        message_elements += [f"<b>{_("my_info_header")}</b>",
                             ""]

    if matching:
        username = user.active_usernames[0] or user.username

        message_elements += [f"@{username}"]
    else:
        message_elements = [f"{_("name")}: {user.first_name}"]

    if age is not None:
        message_elements += [f"{_("age")}: {age}"]

    if gender is not None:
        message_elements += [f"{_("gender")}: {_(gender)}"]

    if interests is not None:
        message_elements += [f"{_("interests")}: {", ".join(interests)}"]

    message_elements += [f"{_("country")}: {country}",
                         f"{_("city")}: {city}"]

    if bio is not None:
        message_elements += [f"{_("bio")}: {bio}"]

    return "\n".join(message_elements)


async def location_to_text(location: aiogram.types.Location) -> dict:
    user_location = await osm.process_location(location.latitude,
                                               location.longitude)

    country, city = user_location["country"], user_location["city"]

    text = f"<b>{_("memorized")}: {country}, {city}</b>"

    if country is None:
        text = f"<b>{_("cannot_find_country")}</b>"

    if city is None:
        text = f"<b>{_("cannot_find_city")}</b>"

    return {"success": (country is not None) and (city is not None),
            "text": text,
            "country": country,
            "city": city}


async def country_to_text(country: str) -> dict:
    found_country = await osm.get_country(country)

    if found_country is not None:
        text = f"<b>🏙 {found_country["name"]}! {_("want_to_country")}</b>"
    else:
        text = f"<b>{_("invalid_country")}</b>"

    return {
        "success": found_country is not None,
        "text": text,
        "country": found_country
    }


async def city_to_text(country: str,
                       city: str) -> dict:
    found_city = await osm.get_city(country, city)

    if found_city is not None:
        text = f"<b>🦊 {found_city["name"]} — {_("nice_city")}!</b>"
    else:
        text = f"<b>{_("invalid_city")}</b>"

    return {
        "success": found_city is not None,
        "text": text,
        "city": found_city
    }


async def travel_to_message(travel: dict,
                            user_id: int,
                            bot: Bot) -> dict:
    message_elements = [f"<b>{_("travel")} «{travel["name"]}»</b>"]

    if travel["description"] is not None:
        message_elements += ["",
                             f"💬 {_("description")}: {travel["description"]}"]

    if travel["locations"]:
        message_elements += ["",
                             f"<b>{_("locations_list")}</b>"]

    for location in travel["locations"]:
        start_date = location["start_date"].strftime("%d.%m.%Y")
        end_date = location["end_date"].strftime("%d.%m.%Y")

        if start_date == end_date:
            date_string = start_date
        else:
            date_string = f"{start_date} - {end_date}"

        message_elements += [f"{location["country"]}, {location["city"]} ({date_string})"]

    if travel["participants"]:
        message_elements += ["",
                             f"<b>{_("participants_list")}</b>"]

    for participant in travel["participants"]:
        try:
            user = await bot.get_chat(participant["user_id"])

            emoji = "⭐️" if travel["creator_id"] == participant["user_id"] else "👤"

            message_elements += [f"{emoji} {user.full_name}"]
        except:
            message_elements += [f"{participant["user_id"]}"]

    can_modify = travel["creator_id"] == user_id

    final_keyboard = [
        [
            InlineKeyboardButton(text=_("travel_notes_button"),
                                 callback_data=cb.TravelNotes(travel_id=travel["id"]).pack()),

            # InlineKeyboardButton(text=_("travel_route"),
            #                      callback_data=cb.TravelRoute(travel_id=travel["id"]).pack()),

            InlineKeyboardButton(text=_("locations_page_button"),
                                 callback_data=cb.TravelLocationsMenu(travel_id=travel["id"]).pack())
        ],
        [
            InlineKeyboardButton(text=_("invite_to_travel_button"),
                                 switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                                     query=travel["id"],
                                     allow_user_chats=True,
                                     allow_group_chats=True
                                 ))
        ]
    ]

    if can_modify:
        final_keyboard += [
            [
                InlineKeyboardButton(text=_("edit_button"),
                                     callback_data=cb.EditTravelPage(travel_id=travel["id"]).pack()),

                InlineKeyboardButton(text=_("delete_button"),
                                     callback_data=cb.DeleteTravel(travel_id=travel["id"],
                                                                   confirmed=False).pack())
            ]
        ]

    final_keyboard += [keyboards.back_to_my_travels]

    return {
        "can_modify": can_modify,
        "text": "\n".join(message_elements),
        "reply_markup": InlineKeyboardMarkup(inline_keyboard=final_keyboard)
    }


async def location_to_message(location: Location,
                              travel: dict,
                              user_id: int,
                              mode: str):
    weather = await get_weather(float(location.latitude), float(location.longitude))

    text = (f"<b>📌 {location.country}, {location.city}</b>\n"
            f"\n"
            f"📅 {_("start_date")}: {location.start_date.strftime("%d.%m.%Y")}\n"
            f"📅 {_("end_date")}: {location.end_date.strftime("%d.%m.%Y")}\n"
            f"\n"
            f"🪟 {_("weather")}: {weather["weather"][0]["description"]}, "
            f"{_("from")} {round(weather["main"]["temp_min"], 1)} {_("to")} {round(weather["main"]["temp_max"], 1)}℃ "
            f"({_("feels_like")} {round(weather["main"]["feels_like"], 1)}℃)")

    location_id = location.id
    travel_id = travel["id"]

    buttons = []

    if mode == "page":
        for place_type in ["landmarks", "hotels", "food"]:
            buttons += [
                [
                    InlineKeyboardButton(text=_(f"get_{place_type}_button"),
                                         callback_data=cb.LocationPlaces(location_id=location_id,
                                                                         place_type=place_type).pack())
                ]
            ]

    if travel["creator_id"] == user_id:
        match mode:
            case "edit":
                buttons += [
                    [
                        InlineKeyboardButton(text=_("edit_start_date_button"),
                                             callback_data=cb.EditLocationDate(
                                                 location_id=location_id,
                                                 date_type="start",
                                                 travel_id=travel_id).pack())
                    ],
                    [
                        InlineKeyboardButton(text=_("edit_end_date_button"),
                                             callback_data=cb.EditLocationDate(
                                                 location_id=location_id,
                                                 date_type="end",
                                                 travel_id=travel_id).pack())
                    ],
                    [
                        InlineKeyboardButton(text=_("delete_button"),
                                             callback_data=cb.DeleteLocation(location_id=location_id,
                                                                             travel_id=travel_id).pack())
                    ]
                ]
            case "page":
                buttons += [
                    [
                        InlineKeyboardButton(text=_("edit_button"),
                                             callback_data=cb.EditLocation(location_id=location_id,
                                                                           travel_id=travel_id).pack())
                    ]
                ]

    match mode:
        case "page":
            back_callback = cb.TravelLocationsMenu(travel_id=travel_id).pack()
        case "edit":
            back_callback = cb.LocationPage(location_id=location_id,
                                            travel_id=travel_id).pack()

    buttons += [
        [
            InlineKeyboardButton(text=_("back_button"),
                                 callback_data=back_callback)
        ]
    ]

    return {
        "text": text,
        "reply_markup": InlineKeyboardMarkup(inline_keyboard=buttons)
    }


async def group_send(bot: Bot,
                     chat_ids: List[int],
                     text: str,
                     reply_markup: InlineKeyboardMarkup) -> None:
    for chat_id in chat_ids:
        await bot.send_message(chat_id,
                               text,
                               reply_markup=reply_markup)


async def add_participant_with_notify(user: User,
                                      travel_id: str,
                                      travel_name: str,
                                      participants: List[int],
                                      bot: Bot) -> None:
    await add_data(UserTravel,
                   check_condition=(
                           (UserTravel.user_id == user.id) & (UserTravel.travel_id == travel_id)),
                   user_id=user.id, travel_id=travel_id)

    await group_send(bot,
                     participants,
                     f"<b>👤 {user.mention_html()} "
                     f"{_("accepted_invite_to")} «{travel_name}»</b>",
                     InlineKeyboardMarkup(inline_keyboard=[
                         [
                             InlineKeyboardButton(text=_("go_to_travel"),
                                                  callback_data=cb.Travel(
                                                      travel_id=travel_id).pack())
                         ]
                     ])
                     )
