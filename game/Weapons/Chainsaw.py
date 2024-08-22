from VegansDeluxe.core import AttachedAction, RegisterWeapon, At, percentage_chance
from VegansDeluxe.core import FreeWeaponAction, MeleeAttack, RegisterEvent, PostTickGameEvent
from VegansDeluxe.core import OwnOnly, EventContext
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import MeleeWeapon


@RegisterWeapon
class Chainsaw(MeleeWeapon):
    id = 'chainsaw'
    name = ls("weapon_chainsaw_name")
    description = ls("weapon_chainsaw_description")

    cubes = 2
    accuracy_bonus = 2
    energy_cost = 2
    damage_bonus = 0

    def __init__(self, session_id: str, entity_id: str):
        super().__init__(session_id, entity_id)
        self.chainsaw = False
        self.turns_active = 0


@AttachedAction(Chainsaw)
class ChainsawAttack(MeleeAttack):
    def func(self, source, target):
        if not self.weapon.chainsaw:
            self.weapon.cubes = 2
            self.weapon.damage_bonus = 0
            self.weapon.accuracy_bonus = 2
            self.weapon.energy_cost = 2
        elif percentage_chance(5):
            self.weapon.chainsaw = False
            self.weapon.turns_active = 0
            self.weapon.cubes = 2
            self.weapon.damage_bonus = 0
            self.weapon.energy_cost = 2
            self.weapon.accuracy_bonus = 2
            self.session.say(ls("weapon_chainsaw_jammed").format(source.name))
            return

        return super().func(source, target)


@AttachedAction(Chainsaw)
class SwitchChainsaw(FreeWeaponAction):
    id = 'switch_chainsaw'
    target_type = OwnOnly()
    priority = -10

    @property
    def name(self):
        return ls("weapon_chainsaw_enable_name")

    def func(self, source, target):
        if self.weapon.chainsaw:
            self.session.say(ls("weapon_chainsaw_active").format(source.name, self.weapon.turns_active))
            return

        self.weapon.chainsaw = True
        self.weapon.turns_active = 5
        self.weapon.cubes = 3
        self.weapon.damage_bonus = 1
        self.weapon.energy_cost = 2
        self.weapon.accuracy_bonus = 2

        self.session.say(ls("weapon_chainsaw_switch_text").format(source.name))

        # Цей код вимкне бензопилу через 5 ходів. Я протестував.
        @At(self.session.id, turn=self.session.turn + 5, event=PostTickGameEvent)
        def apply_explosion(context: EventContext[PostTickGameEvent]):
            self.weapon.chainsaw = False
            self.weapon.cubes = 2
            self.weapon.damage_bonus = 0
            self.weapon.energy_cost = 1
            self.weapon.accuracy_bonus = 2
            context.session.say(ls("weapon_chainsaw_disable_text").format(source.name))
