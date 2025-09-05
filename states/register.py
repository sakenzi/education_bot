from aiogram.fsm.state import State, StatesGroup


class RegisterForm(StatesGroup):
    name = State()
    phone = State()
    direction = State()