import os
from dotenv import load_dotenv

load_dotenv()

# BotFather'dan olgan tokeningizni .env fayliga yozing (pastga qarang)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# HR menejer(lar)ning Telegram ID raqami(lari).
# O'z ID'ingizni bilish uchun @userinfobot ga /start yozing.
# Bir nechta admin bo'lsa, vergul bilan ajrating: "123456,789012"
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! .env faylini tekshiring.")

if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS topilmadi! .env faylida kamida bitta admin ID kiriting.")

# --- Kompaniya ma'lumotlari ---
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

# Mini ilova (Telegram WebApp) manzili.
# GitHub Pages'ga joylashtirgach shu yerga to'liq https havolani kiriting.
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
