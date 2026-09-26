# HR Telegram Bot

Kompaniya uchun HR bot: vakansiyalarga ariza qabul qilish va xodimlar uchun FAQ.

## Imkoniyatlar

- 📋 **Ariza topshirish** — F.I.Sh, telefon, vakansiya va CV (fayl yoki matn) bosqichma-bosqich so'raladi, so'ng HR menejerga avtomatik yuboriladi.
- ❓ **FAQ** — ta'til, ish haqi, ish jadvali va boshqa savollarga tayyor javoblar (inline tugmalar orqali).

## O'rnatish

1. Repositoryni klonlang:
   ```bash
   git clone <repo-url>
   cd hr_bot
   ```

2. Virtual muhit yarating va kutubxonalarni o'rnating:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. `.env.example` faylidan nusxa oling va o'z ma'lumotlaringizni kiriting:
   ```bash
   cp .env.example .env
   ```
   - `BOT_TOKEN` — BotFather'dan olgan token
   - `ADMIN_IDS` — HR menejerning Telegram ID raqami (bilish uchun @userinfobot)

4. Botni ishga tushiring:
   ```bash
   python main.py
   ```

## Loyiha tuzilishi

```
hr_bot/
├── main.py           # Bot ishga tushirish nuqtasi
├── config.py         # Token va admin sozlamalari
├── states.py          # FSM holatlari (ariza jarayoni)
├── keyboards.py       # Barcha tugmalar va FAQ ma'lumotlari
├── handlers/
│   ├── start.py       # /start va asosiy menyu
│   ├── faq.py          # FAQ bo'limi
│   └── apply.py        # Ariza topshirish jarayoni
├── requirements.txt
└── .env.example
```

## Vakansiyalar va FAQ savollarini o'zgartirish

- Vakansiyalar ro'yxati: `keyboards.py` faylidagi `VACANCIES` ro'yxatini tahrirlang.
- FAQ savol-javoblari: `keyboards.py` faylidagi `FAQ_DATA` lug'atini tahrirlang.

## Deploy qilish (serverga joylashtirish)

Bot doimiy ishlashi uchun uni serverda (VPS) yoki quyidagi bepul xizmatlarda ishga tushirishingiz mumkin:
- Railway.app
- Render.com
- PythonAnywhere

`nohup python main.py &` yoki `systemd`/`screen` orqali fon rejimida ishga tushirish tavsiya etiladi.
