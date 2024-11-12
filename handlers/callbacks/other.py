from aiogram.filters.callback_data import CallbackData


class StartGame(CallbackData, prefix="vd_go"):
    pass


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
