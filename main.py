import asyncio
import base64
import binascii
import hashlib
import hmac
import html
import json
import logging
import os
import time
from urllib.parse import parse_qsl

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    MenuButtonWebApp,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()


def esc(v) -> str:
    """Matnni Telegram HTML rejimi uchun xavfsiz qiladi."""
    return html.escape(str(v if v is not None else ""))


# ======================================================================
#  SOZLAMALAR — shu qismni o'zingizga moslab o'zgartiring
# ======================================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Railway'ning Variables bo'limini tekshiring.")
if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS topilmadi! Railway'ning Variables bo'limini tekshiring.")

COMPANY_NAME = "Aloqabor"
COMPANY_TAGLINE = "Aloqa va texnologiyani birlashtiramiz"

# Mini ilova manzili (Railway domeni). "https://" yozilmagan bo'lsa, o'zi qo'shiladi.
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()
if WEBAPP_URL and not WEBAPP_URL.startswith(("http://", "https://")):
    WEBAPP_URL = "https://" + WEBAPP_URL

# ----------------------------------------------------------------------
#  TUGMA MATNLARI — menyudagi tugma va uning handler'i SHU YERDAN olinadi.
#  Emoji yoki matnni faqat shu yerda o'zgartiring — boshqa joyga tegmang.
# ----------------------------------------------------------------------
BTN_VACANCIES = "❕ Bo'sh ish o'rinlari❕"
BTN_PORTFOLIO = "📂 Portfolio"
BTN_FAQ = "❓ FAQ"
BTN_CANCEL = "❌ Bekor qilish"
BTN_CONFIRM = "✅ Tasdiqlash va yuborish"

# "Portfolio" tugmasi bosilganda chiqadigan matn
PORTFOLIO_TEXT = (
    "<b>Aloqabor</b> — outsourcing call-center xizmati va IT avtomatlashtirish "
    "yo'nalishida ishlaydigan kompaniya.\n\n"
    "Jamoamiz turli sohalarda bir qancha muvaffaqiyatli loyihalarni amalga oshirgan:\n\n"
    "🏢 Yirik savdo kompaniyalari uchun call-center xizmati\n"
    "🎓 O'quv markazlari uchun ro'yxatga olish botlari\n"
    "🛒 Onlayn-do'konlar uchun buyurtma qabul qiluvchi botlar\n"
    "🏥 Tibbiyot markazlari uchun navbat botlari\n\n"
    "Loyiha namunalari va batafsil case-study'lar bilan suhbat davomida yaqindan "
    "tanishtiramiz. Jamoamizga qo'shilishga tayyormisiz? 🤝"
)

# Vakansiyalar — shu ro'yxatni o'zgartirish orqali lavozimlarni boshqarasiz
VACANCY_DETAILS = {
    "HR menejeri": {
        "emoji": "👥",
        "desc": "Xodimlarni topish, suhbat o'tkazish va jamoani rivojlantirish bilan shug'ullanasiz.",
        "requirements": [
            "HR sohasida kamida 1 yillik tajriba",
            "Muloqotchan va tashkilotchi",
            "Excel/Google Sheets bilan ishlay olish",
        ],
    },
    "Call-center operatori": {
        "emoji": "🎧",
        "desc": "Mijozlar bilan telefon orqali muloqot qilib, savollariga javob berasiz va buyurtmalarni qayd etasiz.",
        "requirements": [
            "Toza va tushunarli nutq",
            "Sabr-toqatli va diqqatli",
            "Kompyuterda ishlay olish",
        ],
    },
    "IT dasturchi": {
        "emoji": "💻",
        "desc": "Kompaniyaning ichki tizimlari, botlar va avtomatlashtirish loyihalarini yaratasiz va qo'llab-quvvatlaysiz.",
        "requirements": [
            "Python yoki JavaScript bilishi",
            "Git bilan ishlay olish",
            "Mustaqil o'rganishga qiziqish",
        ],
    },
    "Sifat nazorati mutaxassisi (QA)": {
        "emoji": "🔍",
        "desc": "Call-center operatorlarining qo'ng'iroqlarini tinglab, xizmat sifatini baholaysiz.",
        "requirements": [
            "Diqqatlilik va tafsilotlarga e'tibor",
            "Konstruktiv fikr bildira olish",
            "Hisobot yuritish ko'nikmasi",
        ],
    },
    "Loyiha menejeri": {
        "emoji": "📊",
        "desc": "IT avtomatlashtirish loyihalarini rejalashtirasiz va jamoani muvofiqlashtirasiz.",
        "requirements": [
            "Loyihalarni boshqarishda tajriba (afzallik)",
            "Aniq va tizimli fikrlash",
            "Jamoa bilan ishlay olish",
        ],
    },
}
VACANCIES = list(VACANCY_DETAILS.keys())

# FAQ — shu lug'atni o'zgartirish orqali savol-javoblarni boshqarasiz
FAQ_DATA = {
    "interview": {
        "question": "❔ Suhbat jarayoni qanday o'tadi❔",
        "answer": (
            "Ariza yuborganingizdan so'ng, mos nomzodlar bilan HR bo'limi 1–2 ish kuni ichida "
            "bog'lanadi. Suhbat odatda ikki bosqichda o'tadi: avval qisqa telefon suhbati, "
            "so'ngra ofisda (yoki onlayn) yakuniy uchrashuv. Har bir bosqich natijasi haqida "
            "sizga albatta xabar beramiz."
        ),
    },
    "vacation": {
        "question": "❔ Ta'til qanday beriladi❔",
        "answer": (
            "Har bir xodim mehnat qonunchiligiga muvofiq yiliga 24 ish kuni asosiy ta'tilga "
            "ega. Ta'til sanalarini kamida 2 hafta oldin bevosita rahbaringiz va HR bo'limi "
            "bilan kelishib olishingizni tavsiya qilamiz — shunda ish jarayoni uzluksiz davom etadi."
        ),
    },
    "salary": {
        "question": "❔ Ish haqi qachon to'lanadi❔",
        "answer": (
            "Ish haqi har oyning 5- va 20-sanalarida, ikki bosqichda (avans va asosiy qism) "
            "plastik kartangizga o'tkaziladi. Barcha to'lovlar rasmiy mehnat shartnomasi "
            "asosida, kechikishsiz amalga oshiriladi."
        ),
    },
    "schedule": {
        "question": "❔ Ish jadvali qanday❔",
        "answer": (
            "Ofis xodimlari uchun standart jadval — Dushanbadan Jumagacha, 09:00–18:00, "
            "tushlik uchun 1 soatlik tanaffus bilan. Call-center operatorlari uchun smena "
            "jadvali individual tarzda, sizning qulayligingizni hisobga olib tuziladi."
        ),
    },
    "remote": {
        "question": "❔ Masofadan ishlash mumkinmi❔",
        "answer": (
            "IT yo'nalishidagi bir qator lavozimlar uchun gibrid (qisman masofaviy) ish "
            "formati mavjud. Bu bo'lim rahbari va vazifalar xususiyatiga qarab belgilanadi — "
            "suhbat davomida batafsil muhokama qilamiz."
        ),
    },
    "contract": {
        "question": "❔ Mehnat shartnomasi qanday tuziladi❔",
        "answer": (
            "Ishga qabul qilingan kuningizdayoq O'zbekiston mehnat qonunchiligiga muvofiq "
            "rasmiy mehnat shartnomasi tuziladi. Sinov muddati — 3-15 kun, bu davrda ham barcha "
            "ijtimoiy kafolatlar (ta'til, kasallik varaqasi va h.k.) to'liq saqlanadi."
        ),
    },
}


# ======================================================================
#  HOLATLAR (FSM)
# ======================================================================

class ApplyForm(StatesGroup):
    full_name = State()
    phone = State()
    age = State()
    vacancy = State()
    experience = State()
    confirm = State()
    cv_extra = State()


# ======================================================================
#  TUGMALAR (KEYBOARDS)
# ======================================================================

def main_menu():
    rows = [
        [KeyboardButton(text=BTN_VACANCIES)],
        [KeyboardButton(text=BTN_PORTFOLIO), KeyboardButton(text=BTN_FAQ)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def start_inline_kb():
    """/start xabari ostida chiqadigan, mini ilovani darhol ochadigan tugma"""
    if not WEBAPP_URL:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Mini ilovani ochish", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])


def phone_request_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def vacancies_list_kb():
    buttons = [
        [InlineKeyboardButton(text=f"{v['emoji']} {name}", callback_data=f"vac_{i}")]
        for i, (name, v) in enumerate(VACANCY_DETAILS.items())
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def vacancy_detail_kb(index: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Shu lavozimga ariza berish", callback_data=f"apply_{index}")],
        [InlineKeyboardButton(text="⬅️ Ro'yxatga qaytish", callback_data="vac_back")],
    ])


def vacancies_reply_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=name)] for name in VACANCIES],
        resize_keyboard=True, one_time_keyboard=True,
    )


def confirm_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CONFIRM)], [KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def faq_menu_kb():
    buttons = [[InlineKeyboardButton(text=v["question"], callback_data=f"faq_{key}")] for key, v in FAQ_DATA.items()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def faq_back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="faq_back")]])


# ======================================================================
#  HANDLERLAR
# ======================================================================

router = Router()


# ---- Start / Portfolio ----

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, <b>{esc(message.from_user.first_name)}</b>! 👋\n\n"
        f"<b>{COMPANY_NAME}</b> HR botiga xush kelibsiz — karyerangizni biz bilan "
        "boshlashingiz mumkin.\n\n"
        "Bot orqali siz:\n"
        "◈ Mini ilova orqali bir necha soniyada ariza topshirasiz\n"
        "◈ Barcha ochiq lavozimlar bilan tanishasiz\n"
        "◈ Kompaniyamiz portfoliosini ko'rasiz\n"
        "◈ Ish sharoitlari bo'yicha javoblar olasiz\n\n"
        "Boshlash uchun pastdagi tugmalardan birini tanlang 👇",
        reply_markup=main_menu(),
    )
    kb = start_inline_kb()
    if kb:
        await message.answer("Eng tezkor yo'l — mini ilovani shu yerdan oching:", reply_markup=kb)


@router.message(F.text == BTN_PORTFOLIO)
async def company_info(message: Message):
    await message.answer(PORTFOLIO_TEXT, reply_markup=main_menu())


@router.message(F.text == BTN_CANCEL)
async def cancel_anywhere(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi. Asosiy menyuga qaytdingiz.", reply_markup=main_menu())


# ---- FAQ ----

FAQ_INTRO = (
    "❓ <b>Ko'p so'raladigan savollar</b>\n\n"
    "Quyidagi ro'yxatdan sizni qiziqtirgan mavzuni tanlang. Boshqa savolingiz qolsa, "
    "ariza yuborganingizdan so'ng HR bo'limi siz bilan bevosita bog'lanib, barcha "
    "tafsilotlarni tushuntirib beradi."
)


@router.message(F.text == BTN_FAQ)
async def show_faq_menu(message: Message):
    await message.answer(FAQ_INTRO, reply_markup=faq_menu_kb())


@router.callback_query(F.data.startswith("faq_"))
async def faq_answer(callback: CallbackQuery):
    key = callback.data.replace("faq_", "")
    if key == "back":
        await callback.message.edit_text(FAQ_INTRO, reply_markup=faq_menu_kb())
        await callback.answer()
        return
    item = FAQ_DATA.get(key)
    if item:
        await callback.message.edit_text(f"{item['question']}\n\n{item['answer']}", reply_markup=faq_back_kb())
    await callback.answer()


# ---- Vakansiyalar ----

VACANCIES_INTRO = (
    f"💼 <b>Bo'sh ish o'rinlari</b>\n\n"
    f"<b>{COMPANY_NAME}</b> jamoasi faol rivojlanmoqda va hoziroq <b>{{n}}</b> ta "
    "yo'nalishda iqtidorli hamkasblarni kutyapmiz.\n\n"
    "Har bir lavozim tafsilotlarini ko'rish uchun kerakli kartani tanlang — vazifalar, "
    "talablar va ariza berish tugmasi shu yerning o'zida 👇"
).format(n=len(VACANCIES))


@router.message(F.text == BTN_VACANCIES)
async def show_vacancies(message: Message):
    await message.answer(VACANCIES_INTRO, reply_markup=vacancies_list_kb())


@router.callback_query(F.data == "vac_back")
async def back_to_list(callback: CallbackQuery):
    await callback.message.edit_text(VACANCIES_INTRO, reply_markup=vacancies_list_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("vac_"))
async def vacancy_detail(callback: CallbackQuery):
    index = int(callback.data.replace("vac_", ""))
    name = VACANCIES[index]
    v = VACANCY_DETAILS[name]
    requirements = "\n".join(f"• {r}" for r in v["requirements"])
    text = f"{v['emoji']} <b>{name}</b>\n\n{v['desc']}\n\n<b>Asosiy talablar:</b>\n{requirements}"
    await callback.message.edit_text(text, reply_markup=vacancy_detail_kb(index))
    await callback.answer()


# ---- Ariza topshirish (bot ichida, bosqichma-bosqich) ----

@router.callback_query(F.data.startswith("apply_"))
async def start_apply_from_vacancy(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.replace("apply_", ""))
    vacancy_name = VACANCIES[index]
    await state.clear()
    await state.update_data(vacancy=vacancy_name, source="manual")
    await state.set_state(ApplyForm.full_name)
    await callback.message.answer(
        f"📝 <b>{vacancy_name}</b> lavozimiga ariza topshirish jarayonini boshladik.\n"
        "Bu atigi 1 daqiqa vaqtingizni oladi.\n\n"
        "1/5. Iltimos, to'liq ism-sharifingizni kiriting (Familiya Ism):",
    )
    await callback.answer()


@router.message(ApplyForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ApplyForm.phone)
    await message.answer(
        "2/5. Rahmat! Endi telefon raqamingizni yuboring — tugmani bosing "
        "yoki qo'lda kiriting (masalan: +998901234567):",
        reply_markup=phone_request_kb(),
    )


@router.message(ApplyForm.phone, F.contact)
async def get_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await ask_age(message, state)


@router.message(ApplyForm.phone, F.text)
async def get_phone_text(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await ask_age(message, state)


async def ask_age(message: Message, state: FSMContext):
    await state.set_state(ApplyForm.age)
    await message.answer("3/5. Necha yoshdasiz? (faqat raqam bilan kiriting, masalan: 24)")


@router.message(ApplyForm.age)
async def get_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    data = await state.get_data()
    if data.get("vacancy"):
        await ask_experience(message, state)
    else:
        await state.set_state(ApplyForm.vacancy)
        await message.answer("4/5. Qaysi vakansiyaga ariza topshirmoqchisiz?", reply_markup=vacancies_reply_kb())


@router.message(ApplyForm.vacancy)
async def get_vacancy(message: Message, state: FSMContext):
    await state.update_data(vacancy=message.text)
    await ask_experience(message, state)


async def ask_experience(message: Message, state: FSMContext):
    await state.set_state(ApplyForm.experience)
    await message.answer(
        "5/5. Deyarli tugadi! Ta'limingiz va ish tajribangiz haqida qisqacha yozing "
        "(o'quv muassasasi, oldingi ish joylari, ko'nikmalar).\n\n"
        "📎 Agar tayyor CV (rezyume) faylingiz bo'lsa, matn o'rniga shu yerga PDF yoki "
        "Word ko'rinishida yuborishingiz ham mumkin — ikkalasi ham bitta qadam:",
    )


@router.message(ApplyForm.experience, F.document)
async def get_experience_document(message: Message, state: FSMContext):
    await state.update_data(
        cv_type="document",
        cv_file_id=message.document.file_id,
        experience=message.caption if message.caption else "CV fayli orqali yuborildi",
    )
    await show_summary(message, state)


@router.message(ApplyForm.experience, F.text)
async def get_experience_text(message: Message, state: FSMContext):
    await state.update_data(cv_type="text", cv_file_id=None, experience=message.text)
    await show_summary(message, state)


async def show_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(ApplyForm.confirm)
    g = lambda k: esc(data.get(k))
    cv_line = "\n📎 CV fayli: biriktirilgan ✅" if data.get("cv_type") == "document" else ""
    await message.answer(
        "📋 <b>Ma'lumotlaringizni tekshiring</b> — hammasi to'g'rimi?\n\n"
        f"👤 F.I.Sh: {g('full_name')}\n"
        f"📱 Telefon: {g('phone')}\n"
        f"🎂 Yosh: {g('age')}\n"
        f"💼 Vakansiya: {g('vacancy')}\n"
        f"🎓 Ta'lim/tajriba: {g('experience')}"
        f"{cv_line}",
        reply_markup=confirm_kb(),
    )


@router.message(ApplyForm.confirm, F.text == BTN_CONFIRM)
async def confirm_application(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    g = lambda k: esc(data.get(k))
    text = (
        "🆕 <b>Yangi ariza tushdi!</b>\n\n"
        f"👤 F.I.Sh: {g('full_name')}\n"
        f"📱 Telefon: {g('phone')}\n"
        f"🎂 Yosh: {g('age')}\n"
        f"💼 Vakansiya: {g('vacancy')}\n"
        f"🎓 Ta'lim/tajriba: {g('experience')}\n"
        f"🆔 Telegram: @{esc(message.from_user.username or 'yoq')} (ID: {message.from_user.id})\n"
    )
    await notify_admins(bot, text[:4000])
    if data.get("cv_type") == "document":
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_document(admin_id, data.get("cv_file_id"), caption="📎 CV")
            except Exception:
                pass
    await state.clear()
    await message.answer(
        "✅ <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        "HR bo'limi arizangizni ko'rib chiqib, tez orada siz bilan bog'lanadi. "
        "E'tiboringiz uchun rahmat! 🙏",
        reply_markup=main_menu(),
    )


# ---- Mini ilovadan sendData orqali kelgan ariza (zaxira yo'l) ----

@router.message(F.web_app_data)
async def handle_webapp_data(message: Message, state: FSMContext, bot: Bot):
    try:
        payload = json.loads(message.web_app_data.data)
    except (ValueError, AttributeError):
        await message.answer("Ma'lumotlarni o'qishda xatolik yuz berdi. Qaytadan urinib ko'ring.")
        return
    user = {"id": message.from_user.id, "username": message.from_user.username}
    if not await notify_admins(bot, build_admin_text(payload, user)):
        await message.answer("Arizani yuborib bo'lmadi. Keyinroq qayta urinib ko'ring.")
        return
    await state.set_state(ApplyForm.cv_extra)
    await message.answer(
        THANKS.get(payload.get("lang"), THANKS["uz"])
        + "\n\n📎 Xohlasangiz, CV faylingizni shu yerga yuboring.",
        reply_markup=main_menu(),
    )


@router.message(ApplyForm.cv_extra, F.document)
async def cv_extra_doc(message: Message, state: FSMContext, bot: Bot):
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_document(
                admin_id, message.document.file_id,
                caption=f"📎 CV — {esc(message.from_user.full_name)} (ID: {message.from_user.id})",
                parse_mode="HTML",
            )
        except Exception:
            pass
    await state.clear()
    await message.answer("✅ CV qabul qilindi. Rahmat!", reply_markup=main_menu())


# ======================================================================
#  MINI ILOVA UCHUN SERVER (ariza qabul qilish + webapp fayllarini berish)
# ======================================================================

WEBAPP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp")


def verify_init_data(init_data: str, token: str, max_age: int = 172800):
    """Telegram Mini App initData'ni tekshiradi. To'g'ri bo'lsa user (dict) qaytaradi."""
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
        got = pairs.pop("hash", "")
        check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
        secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
        calc = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, got) or time.time() - int(pairs.get("auth_date", 0)) > max_age:
            return None
        return json.loads(pairs.get("user", "{}"))
    except Exception:
        return None


def build_admin_text(p: dict, user: dict) -> str:
    g = lambda k: esc(p.get(k, ""))
    uname = user.get("username")
    resume_line = ""
    if p.get("resume_text"):
        resume_line = f"📝 Rezyume: {g('resume_text')}\n"
    elif p.get("resume_file"):
        resume_line = "📎 Rezyume: fayl biriktirilgan (pastda)\n"
    return (
        "🆕 <b>Yangi ariza (Mini App)</b>\n\n"
        f"💼 Vakansiya: <b>{g('vacancy')}</b>\n"
        f"👤 F.I.Sh: {g('full_name')}\n"
        f"🎂 Tug'ilgan sana: {g('birth_date')} ({g('age')} yosh)\n"
        f"📱 Telefon: {g('phone')}\n"
        f"✉️ Email: {g('email') or '—'}\n"
        f"📍 Yashash joyi: {g('live_region')}, {g('district')}\n"
        f"🏢 Ishlamoqchi bo'lgan hudud: {g('work_region')}\n"
        f"🛠 Tajriba: {g('experience')}\n"
        f"{resume_line}"
        f"💰 Kutilayotgan maosh: {g('expected_salary')}\n"
        f"🆔 Telegram: {'@' + esc(uname) if uname else 'yoq'} (ID: {user.get('id')})"
    )[:4000]


async def notify_admins(bot: Bot, text: str) -> bool:
    sent = False
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
            sent = True
        except Exception as e:
            logging.warning("Adminga yuborib bo'lmadi (%s): %s", admin_id, e)
    return sent


THANKS = {
    "uz": "✅ Arizangiz qabul qilindi! HR bo'limi tez orada siz bilan bog'lanadi.",
    "ru": "✅ Ваша заявка принята! HR-отдел скоро свяжется с вами.",
    "en": "✅ Your application has been received! The HR team will contact you soon.",
}


async def api_apply(request: web.Request):
    bot: Bot = request.app["bot"]
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "bad_json"}, status=400)

    user = verify_init_data(data.get("initData", ""), BOT_TOKEN)
    if not user:
        return web.json_response({"ok": False, "error": "auth"}, status=401)

    p = data.get("payload") or {}

    if not await notify_admins(bot, build_admin_text(p, user)):
        return web.json_response({"ok": False, "error": "delivery"}, status=502)

    resume_file = p.get("resume_file")
    if resume_file and resume_file.get("data"):
        try:
            file_bytes = base64.b64decode(resume_file["data"])
            if len(file_bytes) > 8 * 1024 * 1024:
                raise ValueError("resume too large")
            doc = BufferedInputFile(file_bytes, filename=resume_file.get("name") or "resume.pdf")
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_document(admin_id, doc, caption=f"📎 Rezyume — {esc(p.get('full_name'))}")
                except Exception as e:
                    logging.warning("Rezyume yuborib bo'lmadi (%s): %s", admin_id, e)
        except (binascii.Error, ValueError) as e:
            logging.warning("Rezyume faylini o'qib bo'lmadi: %s", e)

    try:
        await bot.send_message(user["id"], THANKS.get(p.get("lang"), THANKS["uz"]))
    except Exception:
        pass

    return web.json_response({"ok": True})


async def index_page(request: web.Request):
    return web.FileResponse(
        os.path.join(WEBAPP_DIR, "index.html"), headers={"Cache-Control": "no-cache"}
    )


async def start_web_server(bot: Bot):
    app = web.Application(client_max_size=12 * 1024 * 1024)
    app["bot"] = bot
    app.router.add_get("/", index_page)
    app.router.add_get("/health", lambda r: web.Response(text="ok"))
    app.router.add_post("/api/apply", api_apply)
    app.router.add_static("/", WEBAPP_DIR, show_index=False)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080"))).start()


# ======================================================================
#  ISHGA TUSHIRISH
# ======================================================================

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await start_web_server(bot)
    if WEBAPP_URL:
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(text="Karyera", web_app=WebAppInfo(url=WEBAPP_URL))
            )
        except Exception as e:
            logging.warning("Menyu tugmasini o'rnatib bo'lmadi: %s", e)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
