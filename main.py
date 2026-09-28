import asyncio
import hashlib
import hmac
import html
import json
import logging
import os
import time
from urllib.parse import parse_qsl

from aiogram import Bot, Dispatcher, Router, F
from aiohttp import web
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    MenuButtonWebApp,
)
from dotenv import load_dotenv

load_dotenv()

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
COMPANY_DESCRIPTION = (
    "Aloqabor — outsourcing call-center xizmati va IT avtomatlashtirish "
    "yo'nalishida ishlaydigan kompaniya.\n\n"
    "📞 <b>Call-center xizmatlari</b> — mijozlar bilan aloqa, buyurtmalarni qabul qilish, "
    "qo'llab-quvvatlash xizmatini boshqa kompaniyalar uchun outsourcing asosida yuritamiz.\n\n"
    "⚙️ <b>IT avtomatlashtirish</b> — biznes-jarayonlarni avtomatlashtirish, botlar, "
    "CRM va ichki tizimlarni ishlab chiqamiz."
)

# Mini ilova (Telegram WebApp) manzili. GitHub Pages'ga joylashtirgach shu yerga to'liq https havolani kiriting.
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

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
    "about": {
        "question": "🏢 Aloqabor nima bilan shug'ullanadi?",
        "answer": (
            "Aloqabor ikki yo'nalishda ishlaydi: boshqa kompaniyalar uchun outsourcing "
            "asosida call-center xizmati ko'rsatish va biznes-jarayonlarni IT orqali "
            "avtomatlashtirish (botlar, CRM, ichki tizimlar)."
        ),
    },
    "vacation": {
        "question": "🏖 Ta'til qanday beriladi?",
        "answer": (
            "Har bir xodim yiliga 24 ish kuni oddiy ta'tilga huquqli. "
            "Ta'til so'rovini kamida 2 hafta oldin HR bo'limiga yuborish tavsiya etiladi."
        ),
    },
    "salary": {
        "question": "💰 Ish haqi qachon to'lanadi?",
        "answer": "Ish haqi har oyning 5- va 20-sanalarida ikki qismga bo'lib to'lanadi (avans va asosiy qism).",
    },
    "schedule": {
        "question": "🕘 Ish jadvali qanday?",
        "answer": (
            "Standart ish jadvali: Dushanba-Juma, 09:00 - 18:00, tushlik uchun 1 soat tanaffus. "
            "Call-center operatorlari uchun smena jadvali alohida belgilanadi."
        ),
    },
    "remote": {
        "question": "🏠 Masofadan ishlash mumkinmi?",
        "answer": (
            "IT yo'nalishidagi ba'zi lavozimlar uchun gibrid formatda ishlash imkoniyati mavjud. "
            "Bo'lim rahbaringiz bilan kelishib olishingiz kerak."
        ),
    },
    "contract": {
        "question": "📄 Mehnat shartnomasi qanday tuziladi?",
        "answer": (
            "Ish boshlangan kuni HR bo'limi bilan rasmiy mehnat shartnomasi tuziladi, "
            "sinov muddati 3 oyni tashkil qiladi."
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
    cv = State()
    confirm = State()
    cv_extra = State()


# ======================================================================
#  TUGMALAR (KEYBOARDS)
# ======================================================================

def main_menu():
    rows = []
    if WEBAPP_URL:
        rows.append([KeyboardButton(text="🚀 Mini ilovani ochish", web_app=WebAppInfo(url=WEBAPP_URL))])
    rows.append([KeyboardButton(text="💼 Bo'sh ish o'rinlari")])
    rows.append([KeyboardButton(text="🏢 Kompaniya haqida"), KeyboardButton(text="❓ FAQ")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


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
        keyboard=[[KeyboardButton(text="✅ Tasdiqlash va yuborish")], [KeyboardButton(text="❌ Bekor qilish")]],
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


# ---- Start / Kompaniya ----

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, {esc(message.from_user.full_name)}! 👋\n\n"
        f"Men <b>{COMPANY_NAME}</b> kompaniyasining HR botiman.\n\n"
        "💼 Bo'sh ish o'rinlari bilan tanishishingiz\n"
        "🚀 Mini ilova orqali qulay tarzda ariza topshirishingiz\n"
        "❓ Ish sharoitlari haqidagi savollaringizga javob olishingiz mumkin.\n\n"
        "Pastdagi menyudan kerakli bo'limni tanlang 👇",
        reply_markup=main_menu(),
    )


@router.message(F.text == "🏢 Kompaniya haqida")
async def company_info(message: Message):
    await message.answer(
        f"<b>{COMPANY_NAME}</b>\n<i>{COMPANY_TAGLINE}</i>\n\n{COMPANY_DESCRIPTION}",
        reply_markup=main_menu(),
    )


@router.message(F.text == "❌ Bekor qilish")
async def cancel_anywhere(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi. Asosiy menyuga qaytdingiz.", reply_markup=main_menu())


# ---- FAQ ----

@router.message(F.text == "❓ FAQ")
async def show_faq_menu(message: Message):
    await message.answer("Quyidagi savollardan birini tanlang:", reply_markup=faq_menu_kb())


@router.callback_query(F.data.startswith("faq_"))
async def faq_answer(callback: CallbackQuery):
    key = callback.data.replace("faq_", "")
    if key == "back":
        await callback.message.edit_text("Quyidagi savollardan birini tanlang:", reply_markup=faq_menu_kb())
        await callback.answer()
        return
    item = FAQ_DATA.get(key)
    if item:
        await callback.message.edit_text(f"{item['question']}\n\n{item['answer']}", reply_markup=faq_back_kb())
    await callback.answer()


# ---- Vakansiyalar ----

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
    text = f"{v['emoji']} <b>{name}</b>\n\n{v['desc']}\n\n<b>Asosiy talablar:</b>\n{requirements}"
    await callback.message.edit_text(text, reply_markup=vacancy_detail_kb(index))
    await callback.answer()


# ---- Ariza topshirish ----

@router.callback_query(F.data.startswith("apply_"))
async def start_apply_from_vacancy(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.replace("apply_", ""))
    vacancy_name = VACANCIES[index]
    await state.clear()
    await state.update_data(vacancy=vacancy_name, source="manual")
    await state.set_state(ApplyForm.full_name)
    await callback.message.answer(
        f"<b>{vacancy_name}</b> lavozimiga ariza topshirish jarayonini boshladik.\n\n"
        "Iltimos, to'liq ism-sharifingizni kiriting (Familiya Ism):",
    )
    await callback.answer()


@router.message(ApplyForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ApplyForm.phone)
    await message.answer(
        "Rahmat! Endi telefon raqamingizni yuboring (tugmani bosing yoki qo'lda kiriting, masalan: +998901234567):",
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
    await message.answer("Necha yoshdasiz? (faqat raqam bilan kiriting, masalan: 24)")


@router.message(ApplyForm.age)
async def get_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    data = await state.get_data()
    if data.get("vacancy"):
        await ask_experience(message, state)
    else:
        await state.set_state(ApplyForm.vacancy)
        await message.answer("Qaysi vakansiyaga ariza topshirmoqchisiz?", reply_markup=vacancies_reply_kb())


@router.message(ApplyForm.vacancy)
async def get_vacancy(message: Message, state: FSMContext):
    await state.update_data(vacancy=message.text)
    await ask_experience(message, state)


async def ask_experience(message: Message, state: FSMContext):
    await state.set_state(ApplyForm.experience)
    await message.answer(
        "Ta'limingiz va ish tajribangiz haqida qisqacha yozing "
        "(o'quv muassasasi, oldingi ish joylari, ko'nikmalar):",
    )


@router.message(ApplyForm.experience)
async def get_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(ApplyForm.cv)
    await message.answer(
        "So'nggi qadam: CV (rezyume) faylingizni yuboring (PDF/Word) "
        "yoki o'zingiz haqingizda qo'shimcha matn ko'rinishida yozing:",
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
        f"🎂 Yosh: {data.get('age')}\n"
        f"💼 Vakansiya: {data.get('vacancy')}\n"
        f"🎓 Ta'lim/tajriba: {data.get('experience')}\n"
        f"📄 CV: {cv_preview}\n\nHammasi to'g'rimi?",
        reply_markup=confirm_kb(),
    )


@router.message(ApplyForm.confirm, F.text == "✅ Tasdiqlash va yuborish")
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
    if data.get("cv_type") != "document":
        text += f"\n📄 Qo'shimcha:\n{g('cv_text')}"
    await notify_admins(bot, text[:4000])
    if data.get("cv_type") == "document":
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_document(admin_id, data.get("cv_file_id"), caption="📎 CV")
            except Exception:
                pass
    await state.clear()
    await message.answer(
        "✅ Arizangiz muvaffaqiyatli qabul qilindi! HR bo'limi tez orada siz bilan bog'lanadi.\n\nRahmat! 🙏",
        reply_markup=main_menu(),
    )


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
esc = lambda v: html.escape(str(v if v is not None else ""))


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
    return (
        "🆕 <b>Yangi ariza (Mini App)</b>\n\n"
        f"💼 Vakansiya: <b>{g('vacancy')}</b>\n"
        f"👤 F.I.Sh: {g('full_name')}\n"
        f"🎂 Tug'ilgan sana: {g('birth_date')} ({g('age')} yosh)\n"
        f"📱 Telefon: {g('phone')}\n"
        f"✉️ Email: {g('email')}\n"
        f"📍 Yashash joyi: {g('live_region')}, {g('district')}\n"
        f"🏢 Ish joyi: {g('work_region')} — {g('branch')}\n"
        f"🎓 Ta'lim: {g('education')}\n"
        f"🛠 Tajriba: {g('experience')}\n"
        f"📝 Qo'shimcha: {g('about') or '—'}\n"
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
        user = verify_init_data(data.get("initData", ""), BOT_TOKEN)
        if not user:
            return web.json_response({"ok": False, "error": "auth"}, status=401)
        p = data.get("payload") or {}
        if not await notify_admins(bot, build_admin_text(p, user)):
            return web.json_response({"ok": False, "error": "delivery"}, status=502)
        try:
            await bot.send_message(user["id"], THANKS.get(p.get("lang"), THANKS["uz"]))
        except Exception:
            pass
        return web.json_response({"ok": True})
    except Exception:
        logging.exception("api_apply xatosi")
        return web.json_response({"ok": False}, status=400)


async def index_page(request: web.Request):
    return web.FileResponse(
        os.path.join(WEBAPP_DIR, "index.html"), headers={"Cache-Control": "no-cache"}
    )


async def start_web_server(bot: Bot):
    app = web.Application(client_max_size=1024 * 1024)
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
