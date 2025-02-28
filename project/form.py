from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    first_name: str = State()
    second_name: str = State()
    group: str = State()

