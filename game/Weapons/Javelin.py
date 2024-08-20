from VegansDeluxe.core import AttachedAction, RegisterWeapon
from VegansDeluxe.core import MeleeAttack, RangedAttack
from VegansDeluxe.core import Entity
from VegansDeluxe.core import Session
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import MeleeWeapon

from VegansDeluxe.core import Enemies, Distance
from VegansDeluxe.core import State, PostDamageGameEvent, OwnOnly, DecisiveStateAction

@RegisterWeapon
class Javelin(MeleeWeapon):
    id = 'javelin'
    name = ls("weapon_javelin_name")
    description = ls("weapon_javelin_description")

    cubes = 3
    accuracy_bonus = 2
    energy_cost = 2
    damage_bonus = 0

@AttachedAction(Javelin)
class JavelinAttack(MeleeAttack):
    pass


@AttachedAction(Javelin)
class JavelinThrow(RangedAttack):
    id = 'throw'
    name = ls("weapon_javelin_throw_name")
    target_type = Enemies(distance=Distance.ANY)

    def __init__(self, session: Session, source: Entity, weapon: Javelin):
        super().__init__(session, source, weapon)
        self.damage_bonus = 1

    def func(self, source, target):
        post_damage = self.publish_post_damage_event(source, target, self.damage_bonus)
        target.inbound_dmg.add(source, post_damage, self.session.turn)
        source.outbound_dmg.add(source, post_damage, self.session.turn)

        self.session.say(ls("javelin_throw_text").format(source.name, post_damage, target.name))

        state = source.get_state('knocked-weapon')
        state.weapon = source.weapon
        source.weapon = None 

    def publish_post_damage_event(self, source, target, damage):
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        self.event_manager.publish(message)
        return message.damage


