from aiogram.fsm.state import StatesGroup, State


class UserInfoForm(StatesGroup):
    country = State()
    city = State()
    age = State()
    bio = State()
    interests = State()
    gender = State()


class UserTravelForm(StatesGroup):
    country = State()
    city = State()
    name = State()
    description = State()
    start_date = State()
    end_date = State()


class CreateLocationForm(StatesGroup):
    country = State()
    city = State()
    start_date = State()
    end_date = State()


class LocationEditing(StatesGroup):
    date = State()


class AddingTravelNote(StatesGroup):
    note = State()
    name = State()
    is_private = State()


class EditingUserInfo(StatesGroup):
    in_progress = State()


class EditingTravel(StatesGroup):
    in_progress = State()


class IdleUser(StatesGroup):
    idle = State()
