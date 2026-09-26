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
