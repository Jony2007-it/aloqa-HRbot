from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        "Men kompaniyamizning HR botiman. Sizga qanday yordam bera olaman?\n\n"
        "📋 Vakansiyaga ariza topshirmoqchi bo'lsangiz — pastdagi tugmani bosing.\n"
        "❓ Ish sharoitlari haqida savolingiz bo'lsa — FAQ bo'limiga o'ting.",
        reply_markup=main_menu(),
    )


@router.message(F.text == "❌ Bekor qilish")
async def cancel_anywhere(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi. Asosiy menyuga qaytdingiz.", reply_markup=main_menu())
