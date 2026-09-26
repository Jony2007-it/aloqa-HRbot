from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import ApplyForm
from keyboards import main_menu, phone_request_kb, vacancies_kb, confirm_kb
from config import ADMIN_IDS

router = Router()


@router.message(F.text == "📋 Vakansiyaga ariza topshirish")
async def start_apply(message: Message, state: FSMContext):
    await state.set_state(ApplyForm.full_name)
    await message.answer(
        "Ariza topshirish jarayonini boshladik.\n\n"
        "Iltimos, to'liq ism-sharifingizni kiriting (Familiya Ism):",
    )


@router.message(ApplyForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ApplyForm.phone)
    await message.answer(
        "Rahmat! Endi telefon raqamingizni yuboring "
        "(tugmani bosing yoki qo'lda kiriting, masalan: +998901234567):",
        reply_markup=phone_request_kb(),
    )


@router.message(ApplyForm.phone, F.contact)
async def get_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await ask_vacancy(message, state)


@router.message(ApplyForm.phone, F.text)
async def get_phone_text(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await ask_vacancy(message, state)


async def ask_vacancy(message: Message, state: FSMContext):
    await state.set_state(ApplyForm.vacancy)
    await message.answer(
        "Qaysi vakansiyaga ariza topshirmoqchisiz?",
        reply_markup=vacancies_kb(),
    )


@router.message(ApplyForm.vacancy)
async def get_vacancy(message: Message, state: FSMContext):
    await state.update_data(vacancy=message.text)
    await state.set_state(ApplyForm.cv)
    await message.answer(
        "So'nggi qadam: CV (rezyume) faylingizni yuboring (PDF/Word) "
        "yoki o'zingiz haqingizda qisqacha matn ko'rinishida yozing:",
    )


@router.message(ApplyForm.cv, F.document)
async def get_cv_document(message: Message, state: FSMContext):
    await state.update_data(cv_type="document", cv_file_id=message.document.file_id, cv_text=None)
    await show_summary(message, state)


@router.message(ApplyForm.cv, F.text)
async def get_cv_text(message: Message, state: FSMContext):
    await state.update_data(cv_type="text", cv_file_id=None, cv_text=message.text)
    await show_summary(message, state)


async def show_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    cv_preview = "📎 Fayl biriktirildi" if data.get("cv_type") == "document" else data.get("cv_text")

    await state.set_state(ApplyForm.confirm)
    await message.answer(
        "Ma'lumotlaringizni tekshiring:\n\n"
        f"👤 F.I.Sh: {data.get('full_name')}\n"
        f"📱 Telefon: {data.get('phone')}\n"
        f"💼 Vakansiya: {data.get('vacancy')}\n"
        f"📄 CV: {cv_preview}\n\n"
        "Hammasi to'g'rimi?",
        reply_markup=confirm_kb(),
    )


@router.message(ApplyForm.confirm, F.text == "✅ Tasdiqlash va yuborish")
async def confirm_application(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    text = (
        "🆕 <b>Yangi ariza tushdi!</b>\n\n"
        f"👤 F.I.Sh: {data.get('full_name')}\n"
        f"📱 Telefon: {data.get('phone')}\n"
        f"💼 Vakansiya: {data.get('vacancy')}\n"
        f"🆔 Telegram: @{message.from_user.username or 'yoq'} (ID: {message.from_user.id})\n"
    )

    for admin_id in ADMIN_IDS:
        try:
            if data.get("cv_type") == "document":
                await bot.send_document(
                    admin_id, data.get("cv_file_id"), caption=text, parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    admin_id, text + f"\n📄 CV:\n{data.get('cv_text')}", parse_mode="HTML"
                )
        except Exception:
            pass  # Admin bot bilan hali /start bosmagan bo'lishi mumkin

    await state.clear()
    await message.answer(
        "✅ Arizangiz muvaffaqiyatli qabul qilindi! HR bo'limi tez orada siz bilan bog'lanadi.\n\n"
        "Rahmat! 🙏",
        reply_markup=main_menu(),
    )
