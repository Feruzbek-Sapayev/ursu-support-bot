from aiogram.filters.state import StatesGroup, State


class Test(StatesGroup):
    Q1 = State()
    Q2 = State()


class AdminState(StatesGroup):
    are_you_sure = State()
    ask_ad_content = State()

class SignUp(StatesGroup):
    full_name = State()
    phone_number = State()

class UserState(StatesGroup):
    main = State()
    application = State()
    chat = State()

class AdminsState(StatesGroup):
    chat = State()