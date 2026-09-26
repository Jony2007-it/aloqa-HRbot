from aiogram.fsm.state import State, StatesGroup


class ApplyForm(StatesGroup):
    """Vakansiyaga ariza topshirish jarayonining bosqichlari"""
    full_name = State()      # F.I.Sh
    phone = State()          # Telefon raqami
    vacancy = State()        # Qaysi vakansiyaga
    cv = State()              # CV (fayl yoki matn ko'rinishida)
    confirm = State()        # Tasdiqlash
