from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

import config


# --- Asosiy menyu ---
def main_menu():
    rows = []

    if config.WEBAPP_URL:
        rows.append([
            KeyboardButton(
                text="🚀 Mini ilovani ochish",
                web_app=WebAppInfo(url=config.WEBAPP_URL),
            )
        ])

    rows.append([KeyboardButton(text="💼 Bo'sh ish o'rinlari")])
    rows.append([
        KeyboardButton(text="🏢 Kompaniya haqida"),
        KeyboardButton(text="❓ FAQ"),
    ])

    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# --- Telefon raqamini yuborish tugmasi ---
def phone_request_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return kb


# --- Vakansiyalar (tafsilotlari bilan) ---
VACANCY_DETAILS = {
    "HR menejeri": {
        "emoji": "👥",
        "desc": (
            "Xodimlarni topish, suhbat o'tkazish va jamoani rivojlantirish bilan "
            "shug'ullanasiz."
        ),
        "requirements": [
            "HR sohasida kamida 1 yillik tajriba",
            "Muloqotchan va tashkilotchi",
            "Excel/Google Sheets bilan ishlay olish",
        ],
    },
    "Call-center operatori": {
        "emoji": "🎧",
        "desc": (
            "Mijozlar bilan telefon orqali muloqot qilib, savollariga javob berasiz "
            "va buyurtmalarni qayd etasiz."
        ),
        "requirements": [
            "Toza va tushunarli nutq",
            "Sabr-toqatli va diqqatli",
            "Kompyuterda ishlay olish",
        ],
    },
    "IT dasturchi": {
        "emoji": "💻",
        "desc": (
            "Kompaniyaning ichki tizimlari, botlar va avtomatlashtirish loyihalarini "
            "yaratasiz va qo'llab-quvvatlaysiz."
        ),
        "requirements": [
            "Python yoki JavaScript bilishi",
            "Git bilan ishlay olish",
            "Mustaqil o'rganishga qiziqish",
        ],
    },
    "Sifat nazorati mutaxassisi (QA)": {
        "emoji": "🔍",
        "desc": (
            "Call-center operatorlarining qo'ng'iroqlarini tinglab, xizmat sifatini "
            "baholaysiz va yaxshilash bo'yicha tavsiyalar berasiz."
        ),
        "requirements": [
            "Diqqatlilik va tafsilotlarga e'tibor",
            "Konstruktiv fikr bildira olish",
            "Hisobot yuritish ko'nikmasi",
        ],
    },
    "Loyiha menejeri": {
        "emoji": "📊",
        "desc": (
            "IT avtomatlashtirish loyihalarini rejalashtirasiz, jamoani muvofiqlashtirasiz "
            "va muddatlarga rioya qilinishini nazorat qilasiz."
        ),
        "requirements": [
            "Loyihalarni boshqarishda tajriba (afzallik)",
            "Aniq va tizimli fikrlash",
            "Jamoa bilan ishlay olish",
        ],
    },
}

VACANCIES = list(VACANCY_DETAILS.keys())


def vacancies_list_kb():
    """Bo'sh ish o'rinlari ro'yxati - inline tugmalar"""
    buttons = [
        [InlineKeyboardButton(
            text=f"{v['emoji']} {name}",
            callback_data=f"vac_{i}",
        )]
        for i, (name, v) in enumerate(VACANCY_DETAILS.items())
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def vacancy_detail_kb(index: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Shu lavozimga ariza berish", callback_data=f"apply_{index}")],
        [InlineKeyboardButton(text="⬅️ Ro'yxatga qaytish", callback_data="vac_back")],
    ])


def vacancies_reply_kb():
    """Ariza jarayonida vakansiya tanlash uchun (matn orqali javob berish uchun)"""
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=name)] for name in VACANCIES],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return kb


# --- Tasdiqlash / bekor qilish ---
def confirm_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Tasdiqlash va yuborish")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return kb


# --- FAQ inline tugmalari ---
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
        "answer": (
            "Ish haqi har oyning 5- va 20-sanalarida ikki qismga bo'lib to'lanadi "
            "(avans va asosiy qism)."
        ),
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
            "IT yo'nalishidagi ba'zi lavozimlar uchun gibrid formatda ishlash imkoniyati "
            "mavjud. Bo'lim rahbaringiz bilan kelishib olishingiz kerak."
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


def faq_menu_kb():
    buttons = [
        [InlineKeyboardButton(text=v["question"], callback_data=f"faq_{key}")]
        for key, v in FAQ_DATA.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def faq_back_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="faq_back")]]
    )
