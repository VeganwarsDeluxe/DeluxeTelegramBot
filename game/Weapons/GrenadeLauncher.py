from VegansDeluxe.core.Translator.LocalizedList import LocalizedList
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon
from VegansDeluxe.core import RangedAttack
from VegansDeluxe.core import AttachedAction, RegisterWeapon
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core import Session, Entity, DecisiveItem, Enemies
from VegansDeluxe.core.Events import PostDamageGameEvent
import random


@RegisterWeapon
class GrenadeLauncher(RangedWeapon):
    id = 'grenade_launcher'
    name = ls("weapon_grenade_launcher_name")
    description = ls("weapon_grenade_launcher_description")

    cubes = 4
    accuracy_bonus = 2
    energy_cost = 3


@AttachedAction(GrenadeLauncher)
class GrenadeLauncherAttack(RangedAttack):
    def __init__(self, session: Session, source: Entity, weapon: GrenadeLauncher):
        super().__init__(session, source, weapon)
        self.grenade_action = GrenadeAction(session, source, None)

    def func(self, source, target):
        self.grenade_action.func(source, target)
        source.energy = max(source.energy - self.weapon.energy_cost, 0)


@AttachedAction(GrenadeLauncher)
class GrenadeAction(DecisiveItem):
    # Дуже погано. Item це те що гравець використовує в "Дополнительно", а атака це атака.
    # Краще робіть з Attack, для цього в вас вже є GrenadeLauncherAttack. Якщо в вас не вийде перенести то перенесу я.
    id = 'grenade'
    name = ls("item_grenade_name")
    target_type = Enemies()

    def __init__(self, session: Session, source: Entity, item: None):
        super().__init__(session, source, item)
        self.damage_min = 1
        self.damage_max = 4
        self.range = 2

    def func(self, source, target):
        targets = []
        damage = 0

        for _ in range(self.range):
            target_pool = list(filter(lambda t: t not in targets,
                                      self.get_targets(source, Enemies())))
            if not target_pool:
                continue
            target = random.choice(target_pool)
            damage = random.randint(self.damage_min, self.damage_max)
            post_damage = self.publish_post_damage_event(source, target, damage)
            target.inbound_dmg.add(source, post_damage, self.session.turn)
            source.outbound_dmg.add(source, post_damage, self.session.turn)
            targets.append(target)

        self.session.say(ls("item_grenade_launcher_text")
                         .format(source.name, damage, LocalizedList([t.name for t in targets])))

    def publish_post_damage_event(self, source, target, damage):
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        self.event_manager.publish(message)
        return message.damage
