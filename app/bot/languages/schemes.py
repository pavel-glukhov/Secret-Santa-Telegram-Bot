from pydantic import BaseModel


class MainMenu(BaseModel):
    menu: str
    allowed_actions: str
    language_selection: str
    select_language_answer: str
    start_message: str
    menu_reminder: str
    about_message: str


class ProfileMenuMain(BaseModel):
    menu_message: str
    profile_edit_message: str


class ChangeAddress(BaseModel):
    change_address_first_msg: str
    change_address_second_msg: str
    error: str


class ChangeName(BaseModel):
    change_name_first_msg: str
    change_name_second_msg: str
    change_name_third_msg: str


class ChangeNumber(BaseModel):
    change_number_first_msg: str
    change_number_second_msg: str
    error: str


class DeleteInformation(BaseModel):
    delete_information_first_msg: str
    delete_information_second_msg: str
    error: str


class ProfileMenu(BaseModel):
    main_menu: ProfileMenuMain
    change_address: ChangeAddress
    change_name: ChangeName
    change_number: ChangeNumber
    delete_information: DeleteInformation


class RoomsMenuMain(BaseModel):
    text_control_room: str
    text_control_room_not_scheduler: str
    text_control_room_scheduler: str
    room_closed_uns: str
    room_closed_uns_for_own: str
    room_closed_suc: str


class ActivateRoom(BaseModel):
    activate_msg: str


class ChangeBudget(BaseModel):
    long_budget: str
    change_budget_first_msg: str
    change_budget_second_msg: str


class ChangeOwner(BaseModel):
    user_is_not_exist: str
    error: str
    change_owner_room_first_msg: str
    change_owner_room_second_msg: str


class SettingsMenu(BaseModel):
    main_menu: str


class CreateNewRoom(BaseModel):
    limit: str
    long_room_name: str
    long_budget: str
    create_new_room_first_msg: str
    create_new_room_second_msg: str
    create_new_room_third_msg: str
    create_new_room_forth_msg: str
    create_new_room_additional_msg: str


class DeleteRoom(BaseModel):
    delete_room_first_msg: str
    delete_room_second_msg: str
    error_command_verif: str
    error: str


class Members(BaseModel):
    menu_msg: str


class Subscribe(BaseModel):
    already_joined: str
    number_error: str
    room_is_not_exist_or_closed: str
    subscribe_first_msg: str
    subscribe_second_msg: str
    subscribe_third_msg: str


class Unsubscribe(BaseModel):
    unsubscribe_first_msg: str
    unsubscribe_second_msg: str


class UpdateRoom(BaseModel):
    long_name: str
    update_room_first_msg: str
    update_room_second_msg: str


class RoomsMenu(BaseModel):
    main: RoomsMenuMain
    activate: ActivateRoom
    change_budget: ChangeBudget
    change_owner: ChangeOwner
    settings_menu: SettingsMenu
    create_new_room: CreateNewRoom
    delete_room: DeleteRoom
    members: Members
    subscribe: Subscribe
    unsubscribe: Unsubscribe
    update_room: UpdateRoom


class StartGame(BaseModel):
    time_zone_inf: str
    count_players: str
    time_not_set: str
    time_set_to: str
    expired_datetime: str
    msg_to_send: str
    start_game_first_msg: str
    choose_date: str
    choose_time: str
    days_short: list
    between: str


class GameMenu(BaseModel):
    start_game: StartGame


class WishesMenu(BaseModel):
    your_wishes: str
    new_wishes: str
    changed_wishes: str


class TimeZoneMenu(BaseModel):
    letter_of_country: str
    select_country: str
    select_timezone: str
    selected_timezone: str
    timezone: str
    country: str


class MessageToRecipient(BaseModel):
    first_msg: str
    msg_was_sent: str
    msg_text: str


class MessageToSender(BaseModel):
    first_msg: str
    msg_was_sent: str
    msg_text: str


class CommunicationMenu(BaseModel):
    message_to_recipient: MessageToRecipient
    message_to_sender: MessageToSender


class ButtonsProfileMenu(BaseModel):
    change_profile: str
    profile_edit_name: str
    profile_edit_address: str
    profile_edit_number: str
    change_time_zone: str
    profile_edit_delete_all: str
    change_language: str


class RoomMenuMainButtons(BaseModel):
    menu: str
    return_to_room_menu: str
    root_menu: str


class RoomMenuUserButtons(BaseModel):
    room_show_wish: str
    room_exit: str
    start_game: str
    started_game: str
    room_member_list: str
    configuration: str
    room_activate: str
    room_closed_con_san: str
    room_closed_con_rec: str


class ConfigMenu(BaseModel):
    room_change_name: str
    room_change_budget: str
    room_change_owner: str
    room_delete: str


class SubscribeButtons(BaseModel):
    to_room: str


class RoomMenuButtons(BaseModel):
    main_buttons: RoomMenuMainButtons
    user_room_buttons: RoomMenuUserButtons
    config_menu: ConfigMenu
    subscribe: SubscribeButtons


class GameMenuButtons(BaseModel):
    room_change_game_dt: str
    change_time_zone: str


class WishesMenuButtons(BaseModel):
    change_wish: str


class MainAppMenu(BaseModel):
    create_room: str
    join_room: str
    about: str
    user_profile: str


class Buttons(BaseModel):
    return_back_button: str
    cancel_button: str
    continue_button: str
    menu: str
    reply: str
    profile_menu: ButtonsProfileMenu
    room_menu: RoomMenuButtons
    game_menu: GameMenuButtons
    wishes_menu: WishesMenuButtons
    main_menu: MainAppMenu


class Formatter(BaseModel):
    address_is_not_specified: str
    number_is_not_specified: str
    timezone_is_not_specified: str
    full_name: str
    address: str
    number: str
    timezone: str
    your_room: str


class MessageFormatter(BaseModel):
    address_is_not_specified: str
    number_is_not_specified: str
    message_text: str


class ResultMailing(BaseModel):
    message_text: str
    separator: str


class Messages(BaseModel):
    main_menu: MainMenu
    profile_menu: ProfileMenu
    rooms_menu: RoomsMenu
    game_menu: GameMenu
    wishes_menu: WishesMenu
    time_zone_menu: TimeZoneMenu
    communication_menu: CommunicationMenu


class TranslationMainSchema(BaseModel):
    messages: Messages
    buttons: Buttons
    formatter: Formatter
    message_formatter: MessageFormatter
    result_mailing: ResultMailing
