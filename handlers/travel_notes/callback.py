from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from assistive import callback as cb
from assistive.processors import group_send
from assistive.states import IdleUser, AddingTravelNote
from database.functions import get_data, add_data, delete_data, get_travels
from database.models import Note
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.callback_query(cb.TravelNotes.filter())
async def travel_notes(query: CallbackQuery, callback_data: cb.TravelNotes):
    travel_id = callback_data.travel_id

    notes = (await get_data(Note, ((Note.travel_id == travel_id) & (
            (Note.user_id == query.from_user.id) | (Note.is_private == False))))).all()

    keyboard_buttons = []

    for note in notes:
        keyboard_buttons += [
            [
                InlineKeyboardButton(text=f"{"🔐" if note.is_private else "📒"} {note.name}",
                                     callback_data=cb.TravelNote(travel_id=travel_id,
                                                                 note_id=note.id).pack())
            ]
        ]

    keyboard_buttons += [
        [
            InlineKeyboardButton(text=_("add_note_button"),
                                 callback_data=cb.AddTravelNote(travel_id=travel_id).pack())
        ],
        [
            InlineKeyboardButton(text=_("back_button"),
                                 callback_data=cb.Travel(travel_id=travel_id).pack())
        ]
    ]

    await query.message.answer(f"<b>{_("travel_notes")}</b>",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons))

    await query.message.delete()

    await query.answer()


@router.callback_query(cb.AddTravelNote.filter())
async def add_travel_note(query: CallbackQuery,
                          callback_data: cb.AddTravelNote,
                          state: FSMContext):
    travel_id = callback_data.travel_id

    await query.message.edit_text(f"{_("send_me_note")}",
                                  reply_markup=keyboards.cancel_action)

    await state.set_state(AddingTravelNote.note)

    await state.update_data(travel_id=travel_id)

    await query.answer()


@router.callback_query(cb.NotePrivacy.filter(), StateFilter(AddingTravelNote.is_private))
async def is_private_note(query: CallbackQuery,
                          callback_data: cb.NotePrivacy,
                          state: FSMContext):
    final_info = await state.get_data()

    note = await add_data(model=Note,
                          check_condition=False,
                          user_id=query.from_user.id,
                          is_private=callback_data.is_private,
                          **final_info)

    await query.message.edit_text(f"{_("note_added")}",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text=_("go_to_note"),
                                                               callback_data=cb.TravelNote(
                                                                   travel_id=final_info["travel_id"],
                                                                   note_id=note.id).pack())
                                      ]
                                  ]))

    if not callback_data.is_private:
        travel = (await get_travels(query.from_user.id,
                                    final_info["travel_id"]))[0]

        participants = [x["user_id"] for x in travel["participants"]]

        participants.remove(query.from_user.id)

        await group_send(query.bot,
                         participants,
                         f"<b>📒 {query.from_user.mention_html()} "
                         f"{_("created_note")} «{final_info["name"]}» "
                         f"{_("at_travel")} «{travel["name"]}»</b>",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [
                                 InlineKeyboardButton(text=_("go_to_note"),
                                                      callback_data=cb.TravelNote(travel_id=final_info["travel_id"],
                                                                                  note_id=note.id).pack())
                             ]
                         ]))

    await state.clear()

    await state.set_state(IdleUser.idle)

    await query.answer()


@router.callback_query(cb.TravelNote.filter())
async def travel_note_page(query: CallbackQuery,
                           callback_data: cb.TravelNote):
    travel_note = (await get_data(Note, Note.id == callback_data.note_id)).first()

    text = f"{_("note")} «{travel_note.name}»"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("delete_button"),
                                 callback_data=cb.DeleteNote(travel_id=callback_data.travel_id,
                                                             note_id=callback_data.note_id).pack())
        ],
        [
            InlineKeyboardButton(text=_("back_button"),
                                 callback_data=cb.TravelNotes(
                                     travel_id=callback_data.travel_id).pack())
        ]
    ])

    match travel_note.file_type:
        case "photo":
            await query.message.answer_photo(travel_note.file_id,
                                             caption=text,
                                             reply_markup=keyboard)
        case "video":
            await query.message.answer_video(travel_note.file_id,
                                             caption=text,
                                             reply_markup=keyboard)
        case "document":
            await query.message.answer_document(travel_note.file_id,
                                                caption=text,
                                                reply_markup=keyboard)

    await query.message.delete()

    await query.answer()


@router.callback_query(cb.DeleteNote.filter())
async def delete_note(query: CallbackQuery,
                      callback_data: cb.DeleteNote):
    note_id = callback_data.note_id

    await delete_data(Note, Note.id == note_id)

    await query.message.answer(f"<b>{_("note_deleted")}</b>",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [
                                       InlineKeyboardButton(text=_("back_button"),
                                                            callback_data=cb.TravelNotes(
                                                                travel_id=callback_data.travel_id).pack())
                                   ]
                               ]))

    await query.message.delete()

    await query.answer()
