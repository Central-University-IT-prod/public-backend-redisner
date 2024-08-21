from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from assistive.states import AddingTravelNote
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.message(StateFilter(AddingTravelNote.note))
async def add_note_file(message: Message, state: FSMContext):
    file = message.document or message.photo or message.video

    if file is None:
        await message.delete()

        return

    if isinstance(file, list):
        file = file[-1]

    file_id = file.file_id

    if message.document is not None:
        file_type = "document"

    elif message.photo is not None:
        file_type = "photo"

    else:
        file_type = "video"

    await state.update_data(file_id=file_id,
                            file_type=file_type)

    await message.answer(f"<b>{_("request_name")}</b>")

    await state.set_state(AddingTravelNote.name)


@router.message(StateFilter(AddingTravelNote.name), F.text)
async def add_note_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    await state.set_state(AddingTravelNote.is_private)

    await message.answer(f"<b>{_("request_is_private")}</b>",
                         reply_markup=keyboards.is_private_note)
