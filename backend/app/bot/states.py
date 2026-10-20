from aiogram.fsm.state import State, StatesGroup


class AddProduct(StatesGroup):
    photo = State()
