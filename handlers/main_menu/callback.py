from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from assistive import callback as cb
from assistive.states import IdleUser
from keyboards import keyboards
from localization.localization import Localization

_ = Localization("ru").get

router = Router()


@router.callback_query(cb.MainMenu.filter())
async def start_menu_by_button(query: CallbackQuery):
    await query.message.edit_text(f"<b>{_("menu_text")}</b>",
                                  reply_markup=keyboards.main_menu)

    await query.answer()


@router.callback_query(cb.Cancel.filter())
async def cancel_any_action(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(f"<b>{_("menu_text")}</b>",
                                  reply_markup=keyboards.main_menu)

    await state.clear()

    await state.set_state(IdleUser.idle)

    await query.answer()
