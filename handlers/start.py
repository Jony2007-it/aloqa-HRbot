from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu, FAQ_DATA, faq_menu_kb
import config

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        f"Men <b>{config.COMPANY_NAME}</b> kompaniyasining HR botiman.\n\n"
        "💼 Bo'sh ish o'rinlari bilan tanishishingiz\n"
        "🚀 Mini ilova orqali qulay tarzda ariza topshirishingiz\n"
        "❓ Ish sharoitlari haqidagi savollaringizga javob olishingiz mumkin.\n\n"
        "Pastdagi menyudan kerakli bo'limni tanlang 👇",
        reply_markup=main_menu(),
    )


@router.message(F.text == "🏢 Kompaniya haqida")
async def company_info(message: Message):
    await message.answer(
        f"<b>{config.COMPANY_NAME}</b>\n"
        f"<i>{config.COMPANY_TAGLINE}</i>\n\n"
        f"{config.COMPANY_DESCRIPTION}",
        reply_markup=main_menu(),
    )


@router.message(F.text == "❌ Bekor qilish")
async def cancel_anywhere(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi. Asosiy menyuga qaytdingiz.", reply_markup=main_menu())
