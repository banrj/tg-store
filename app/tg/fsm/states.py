from aiogram.fsm.state import State, StatesGroup


class ClientRegister(StatesGroup):
    name = State()
    age = State()
    email = State()
    esoteric = State()


class AddAdmin(StatesGroup):
    tg_id = State()
    confirmation = State()


class CreateEsoLink(StatesGroup):
    receiver = State()

