from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import assistive.callback as cb
from localization.localization import Localization

_ = Localization("ru").get

skip_button = InlineKeyboardButton(text=_("skip_button"),
                                   callback_data=cb.Skip().pack())

cancel_button = InlineKeyboardButton(text=_("cancel_button"),
                                     callback_data=cb.Cancel().pack())

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=_("my_travels_button"),
                             callback_data=cb.MyTravels().pack()),
    ],
    [
        InlineKeyboardButton(text=_("my_info_button"),
                             callback_data=cb.MyInfo().pack()),
    ],
    [
        InlineKeyboardButton(text=_("find_travelers"),
                             callback_data=cb.FindTravelers().pack())
    ]
])

gender = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=_("male"),
                             callback_data=cb.Gender(gender="male").pack()),
        InlineKeyboardButton(text=_("female"),
                             callback_data=cb.Gender(gender="female").pack())
    ],
    [
        InlineKeyboardButton(text=_("other"),
                             callback_data=cb.Gender(gender="other").pack())
    ],
    [
        skip_button
    ]
])

travel_buttons = [
    [
        InlineKeyboardButton(text=_("new_travel_button"),
                             callback_data=cb.NewTravel().pack()),
    ],
    [
        InlineKeyboardButton(text=_("back_button"),
                             callback_data=cb.MainMenu().pack())
    ]
]

my_info = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=_("edit_info_button"),
                             callback_data=cb.EditInfoPage().pack())
    ],
    [
        InlineKeyboardButton(text=_("main_menu_button"),
                             callback_data=cb.MainMenu().pack())
    ]
])

edit_info = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=_("edit_user_location_button"),
                             callback_data=cb.EditInfo(param="location").pack()),
    ],
    [
        InlineKeyboardButton(text=_("edit_user_age_button"),
                             callback_data=cb.EditInfo(param="age").pack()),
    ],
    [
        InlineKeyboardButton(text=_("edit_user_interests_button"),
                             callback_data=cb.EditInfo(param="interests").pack()),
    ],
    [
        InlineKeyboardButton(text=_("edit_user_bio_button"),
                             callback_data=cb.EditInfo(param="bio").pack()),
    ],
    [
        InlineKeyboardButton(text=_("back_button"),
                             callback_data=cb.MyInfo().pack()),
    ]
])

after_info_edit = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=_("my_info_button"),
                             callback_data=cb.MyInfo().pack()),
    ]
])

back_to_my_travels = [
    InlineKeyboardButton(text=_("back_button"),
                         callback_data=cb.MyTravels().pack())
]

back_to_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=_("main_menu_button"),
                             callback_data=cb.MainMenu().pack())
    ]
])

is_private_note = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=_("public"),
                             callback_data=cb.NotePrivacy(is_private=False).pack()),

        InlineKeyboardButton(text=_("private"),
                             callback_data=cb.NotePrivacy(is_private=True).pack())
    ]
])

skip_step = InlineKeyboardMarkup(inline_keyboard=[
    [
        skip_button
    ]
])

cancel_action = InlineKeyboardMarkup(inline_keyboard=[
    [
        cancel_button
    ]
])

skip_or_cancel = InlineKeyboardMarkup(inline_keyboard=[
    [
        skip_button
    ],
    [
        cancel_button
    ]
])

request_location = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text=_("send_location_button"),
                       request_location=True)
    ]
],
    one_time_keyboard=True,
    resize_keyboard=True
)
