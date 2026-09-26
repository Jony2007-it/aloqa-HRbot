from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards import (
    VACANCY_DETAILS,
    VACANCIES,
    vacancies_list_kb,
    vacancy_detail_kb,
)

router = Router()


@router.message(F.text == "💼 Bo'sh ish o'rinlari")
async def show_vacancies(message: Message):
    await message.answer(
        f"Hozirda <b>{len(VACANCIES)}</b> ta yo'nalishda mutaxassis qidiryapmiz.\n"
        "Batafsil ma'lumot uchun kerakli lavozimni tanlang:",
        reply_markup=vacancies_list_kb(),
    )


@router.callback_query(F.data == "vac_back")
async def back_to_list(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Hozirda <b>{len(VACANCIES)}</b> ta yo'nalishda mutaxassis qidiryapmiz.\n"
        "Batafsil ma'lumot uchun kerakli lavozimni tanlang:",
        reply_markup=vacancies_list_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("vac_"))
async def vacancy_detail(callback: CallbackQuery):
    index = int(callback.data.replace("vac_", ""))
    name = VACANCIES[index]
    v = VACANCY_DETAILS[name]

    requirements = "\n".join(f"• {r}" for r in v["requirements"])
    text = (
        f"{v['emoji']} <b>{name}</b>\n\n"
        f"{v['desc']}\n\n"
        f"<b>Asosiy talablar:</b>\n{requirements}"
    )

    await callback.message.edit_text(text, reply_markup=vacancy_detail_kb(index))
    await callback.answer()
