from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# --- Asosiy menyu ---
def main_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Vakansiyaga ariza topshirish")],
            [KeyboardButton(text="❓ Ko'p so'raladigan savollar (FAQ)")],
        ],
        resize_keyboard=True,
    )
    return kb


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


# --- Vakansiyalar ro'yxati (o'zingizga moslab o'zgartiring) ---
VACANCIES = [
    "Frontend dasturchi",
    "Backend dasturchi",
    "Marketolog",
    "HR mutaxassisi",
    "Sotuv menejeri",
    "Boshqa",
]


def vacancies_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=v)] for v in VACANCIES],
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
            "Standart ish jadvali: Dushanba-Juma, 09:00 - 18:00, tushlik uchun 1 soat tanaffus."
        ),
    },
    "remote": {
        "question": "🏠 Masofadan ishlash mumkinmi?",
        "answer": (
            "Ba'zi lavozimlar uchun gibrid formatda ishlash imkoniyati mavjud. "
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
