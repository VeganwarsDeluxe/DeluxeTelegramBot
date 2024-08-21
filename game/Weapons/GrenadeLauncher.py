from VegansDeluxe.core.Translator.LocalizedList import LocalizedList
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon
from VegansDeluxe.core import RangedAttack, FreeWeaponAction, RegisterWeapon, Entity, Enemies, OwnOnly, AttachedAction
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Events import PostDamageGameEvent
from VegansDeluxe.core.Sessions import Session

import random


@RegisterWeapon
class GrenadeLauncher(RangedWeapon):
    id = 'grenade_launcher'
    name = ls("weapon_grenade_launcher_name")
    description = ls("weapon_grenade_launcher_description")

    cubes = 2
    energy_cost = 3


@AttachedAction(GrenadeLauncher)
class GrenadeLauncherAttack(RangedAttack):
    def __init__(self, session: Session, source: Entity, weapon: GrenadeLauncher):
        super().__init__(session, source, weapon)
        self.damage = random.randint(1, weapon.cubes)
        self.targets_count = 2

    def func(self, source, target):
        targets = []
        post_damage = 0

        for _ in range(self.targets_count):
            target_pool = list(filter(lambda t: t not in targets,
                                      self.get_targets(source, Enemies())))
            if not target_pool:
                continue
            selected_target = random.choice(target_pool)
            post_damage = self.publish_post_damage_event(source, selected_target, self.damage)
            selected_target.inbound_dmg.add(source, post_damage, self.session.turn)
            source.outbound_dmg.add(source, post_damage, self.session.turn)
            targets.append(selected_target)

        self.session.say(ls("item_grenade_launcher_text")
                         .format(source.name, post_damage, LocalizedList([t.name for t in targets])))

    def publish_post_damage_event(self, source, target, damage):
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        self.event_manager.publish(message)
        return message.damage
