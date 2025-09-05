from aiogram.fsm.state import StatesGroup, State


class TestForm(StatesGroup):
    start = State()
    question = State()
    finished = State()