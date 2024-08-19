from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon
from VegansDeluxe.core import RangedAttack, RegisterWeapon, Entity, AttachedAction
from VegansDeluxe.core.Sessions import Session
from VegansDeluxe.core import Enemies, Distance, PostDamageGameEvent
from VegansDeluxe.core import RegisterState, Every, StateContext, EventContext
from VegansDeluxe.core import PreMoveGameEvent
import random

@RegisterWeapon
class NeedleFan(RangedWeapon):
    id = 'needle_fan'
    name = ls("weapon_needle_fan_name")
    description = ls("weapon_needle_fan_description")

    cubes = 2
    accuracy_bonus = 2
    energy_cost = 2
    damage_bonus = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_needles = 1  # Начальное количество игл

@RegisterState(NeedleFan)
def register(root_context: StateContext[NeedleFan]):

    @Every(root_context.session.id, turns=1, event=PreMoveGameEvent)
    def regenerate_needles(context: EventContext[PreMoveGameEvent]):
        weapon = root_context.entity.get_weapon(NeedleFan)
        if weapon and weapon.current_needles < 1:
            weapon.current_needles = 1
            context.session.say(ls("veer_regenerate_needles_text").format(root_context.entity.name))

@AttachedAction(NeedleFan)
class NeedleFanAttack(RangedAttack):
    target_type = Enemies(distance=Distance.ANY)

    def __init__(self, session: Session, source: Entity, weapon: NeedleFan):
        super().__init__(session, source, weapon)
        self.energy_cost = weapon.energy_cost

    def func(self, source, target):
        if self.weapon.current_needles > 0:
            damage = random.randint(1, 2) * self.weapon.current_needles  # Урон зависит от количества игл
            post_damage = self.publish_post_attack_event(source, target, damage)
            target.inbound_dmg.add(source, post_damage, self.session.turn)
            source.outbound_dmg.add(source, post_damage, self.session.turn)

            self.session.say(ls("veer_attack_text").format(source.name, damage, target.name))

            # Уменьшаем количество игл после атаки
            self.weapon.current_needles = 0  # Очищаем стак игл
        else:
            self.session.say(ls("veer_no_needles_text").format(source.name))

    def publish_post_attack_event(self, source, target, damage):
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        self.event_manager.publish(message)
        return message.damage
