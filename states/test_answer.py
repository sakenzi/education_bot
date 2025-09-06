from aiogram.fsm.state import State, StatesGroup


class TestAnswerState(StatesGroup):
    tests = State()
    current = State()
    correct = State()