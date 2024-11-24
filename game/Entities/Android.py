import random

from VegansDeluxe import rebuild
from VegansDeluxe.core import AttachedAction, Session, ls
from VegansDeluxe.core.Actions.EntityActions import ReloadAction
from VegansDeluxe.rebuild.Skills.ShieldGen import ShieldGenAction
from VegansDeluxe.rebuild.States.Dodge import DodgeAction

from startup import engine
from .NPC import NPC
from .TelegramEntity import TelegramEntity, ApproachAction, SkipTurnAction


class Android(NPC):
    weapon_pool = [
        rebuild.Knife
    ]

    def __init__(self, session_id: str, name=ls("android")):
        # TODO: Localization
        super().__init__(session_id, name)

        self.weapon = self.choose_weapon()

        self.hp = 4
        self.max_hp = 5
        self.max_energy = 5

        self.team = 'android'

    def choose_weapon(self):
        return random.choice(self.weapon_pool)(self.session_id, self.id)

    async def choose_act(self, session: Session[TelegramEntity]):
        await super().choose_act(session)

        dodge_available = engine.action_manager.is_action_available(session, self, DodgeAction.id)
        stimulator_available = engine.action_manager.is_action_available(session, self, rebuild.Stimulator.id)
        shield_available = (engine.action_manager.is_action_available(session, self, rebuild.Shield.id)
                            or engine.action_manager.is_action_available(session, self, ShieldGenAction.id))

        defence_action_available = (dodge_available or shield_available)

        # Check if able to heal.
        if self.hp <= 2 and stimulator_available:
            stimulator_action = engine.action_manager.get_action(session, self, rebuild.Stimulator.id)
            self.items.remove(stimulator_action.item)
            engine.action_manager.queue_action_instance(stimulator_action)
            return

        choice_pool = []

        attack_action = engine.action_manager.get_action(session, self, "attack")
        if not attack_action.targets:
            act = engine.action_manager.get_action(session, self, ApproachAction.id)
            act.target = self
            choice_pool.append(act)
        elif self.hit_chance >= 60:
            attack_action.target = random.choice(attack_action.targets)
            choice_pool.append(attack_action)

        if self.hit_chance < 60:
            reload_action = engine.action_manager.get_action(session, self, ReloadAction.id)
            choice_pool.append(reload_action)

        if choice_pool:
            engine.action_manager.queue_action_instance(random.choice(choice_pool))
            return

        session.say("🤖|The android stands still.")


@AttachedAction(Android)
class ApproachAction(ApproachAction):
    pass


@AttachedAction(Android)
class ReloadAction(ReloadAction):
    pass


@AttachedAction(Android)
class SkipTurnAction(SkipTurnAction):
    pass
