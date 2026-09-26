from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards import faq_menu_kb, faq_back_kb, FAQ_DATA

router = Router()


@router.message(F.text == "❓ Ko'p so'raladigan savollar (FAQ)")
async def show_faq_menu(message: Message):
    await message.answer(
        "Quyidagi savollardan birini tanlang:",
        reply_markup=faq_menu_kb(),
    )


@router.callback_query(F.data.startswith("faq_"))
async def faq_answer(callback: CallbackQuery):
    key = callback.data.replace("faq_", "")

    if key == "back":
        await callback.message.edit_text(
            "Quyidagi savollardan birini tanlang:",
            reply_markup=faq_menu_kb(),
        )
        await callback.answer()
        return

    item = FAQ_DATA.get(key)
    if item:
        await callback.message.edit_text(
            f"{item['question']}\n\n{item['answer']}",
            reply_markup=faq_back_kb(),
        )
    await callback.answer()
