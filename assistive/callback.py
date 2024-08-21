from aiogram.filters.callback_data import CallbackData


class MainMenu(CallbackData, prefix="main_menu"):
    pass


class MyInfo(CallbackData, prefix="my_info"):
    pass


class MyTravels(CallbackData, prefix="my_travels"):
    pass


class NewTravel(CallbackData, prefix="new_travel"):
    pass


class LocationFromProfile(CallbackData, prefix="location_from_profile"):
    pass


class Travel(CallbackData, prefix="travel_page"):
    travel_id: str = None


class FindTravelers(CallbackData, prefix="find_travelers"):
    pass


class Gender(CallbackData, prefix="gender"):
    gender: str


class EditInfoPage(CallbackData, prefix="edit_info"):
    pass


class EditInfo(CallbackData, prefix="edit_user"):
    param: str


class EditTravelPage(CallbackData, prefix="edit_travel_page"):
    travel_id: str


class EditTravel(CallbackData, prefix="edit_travel"):
    travel_id: str
    param: str


class TravelRoute(CallbackData, prefix="travel_route"):
    travel_id: str


class TravelNotes(CallbackData, prefix="travel_notes"):
    travel_id: str


class TravelNote(CallbackData, prefix="travel_note"):
    travel_id: str
    note_id: int


class AddTravelNote(CallbackData, prefix="add_travel_note"):
    travel_id: str


class NotePrivacy(CallbackData, prefix="note_privacy"):
    is_private: bool


class DeleteNote(CallbackData, prefix="delete_note"):
    travel_id: str
    note_id: int
    confirmed: bool = False


class Location(CallbackData, prefix="location"):
    location_id: int


class TravelLocationsMenu(CallbackData, prefix="edit_locations"):
    travel_id: str


class LocationPage(CallbackData, prefix="location_page"):
    travel_id: str
    location_id: int


class EditLocation(CallbackData, prefix="edit_location"):
    travel_id: str
    location_id: int


class EditLocationDate(CallbackData, prefix="edit_date"):
    location_id: int
    date_type: str
    travel_id: str


class LocationPlaces(CallbackData, prefix="location_places"):
    location_id: int
    place_type: str


class DeleteLocation(CallbackData, prefix="delete_location"):
    travel_id: str
    location_id: int
    confirmed: bool = False


class RearrangeLocations(CallbackData, prefix="rearrange_locations"):
    travel_id: str


class AddLocation(CallbackData, prefix="add_location"):
    travel_id: str


class DeleteTravel(CallbackData, prefix="delete_travel"):
    travel_id: str
    confirmed: bool = False


class Skip(CallbackData, prefix="skip"):
    pass


class Cancel(CallbackData, prefix="cancel"):
    pass
