from aiogram.filters.callback_data import CallbackData


# TODO: Don't keep all handlers in other.py. Refactor.


class JoinTeam(CallbackData, prefix="join_team"):
    game_id: str
    team_id: str
    team_type: str


class ChangeLocale(CallbackData, prefix="change_locale"):
    locale: str


class StartGame(CallbackData, prefix="vd_go"):
    pass


class RefreshTeamList(CallbackData, prefix="refresh_teams"):
    game_id: str


class LeaveTeam(CallbackData, prefix="leave_team"):
    game_id: str


class WeaponInfo(CallbackData, prefix="wi"):
    weapon_id: str


class StateInfo(CallbackData, prefix="si"):
    state_id: str


class ChooseWeapon(CallbackData, prefix="cw"):
    game_id: str
    weapon_id: str


class ChooseSkill(CallbackData, prefix="cs"):
    cycle: int
    game_id: str
    skill_id: str


class Additional(CallbackData, prefix="more"):
    game_id: str


class ActionChoice(CallbackData, prefix="act"):
    game_id: str
    action_id: str


class TargetChoice(CallbackData, prefix="tgt"):
    game_id: str
    target_id: str
    index: int


class AnswerChoice(CallbackData, prefix="ans"):
    game_id: str
    question_id: str
    choice_id: str


class Back(CallbackData, prefix="back"):
    game_id: str
