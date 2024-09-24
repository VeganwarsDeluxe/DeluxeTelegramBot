from VegansDeluxe.core import AttachedAction, RegisterWeapon, At, percentage_chance
from VegansDeluxe.core import FreeWeaponAction, MeleeAttack, PostTickGameEvent, Entity, PostDamageGameEvent
from VegansDeluxe.core import OwnOnly, EventContext
from VegansDeluxe.core.Session import Session
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import MeleeWeapon


@RegisterWeapon
class Chainsaw(MeleeWeapon):
    id = 'chainsaw'
    name = ls("weapon_chainsaw_name")
    description = ls("weapon_chainsaw_description")

    def __init__(self, session_id: str, entity_id: str):
        super().__init__(session_id, entity_id)
        self.WoundUp = False
        self.turns_active = 0
        self.cooldown_turn = 0

    def reset_stats(self):
        self.cubes = 2
        self.energy_cost = 2
        self.accuracy_bonus = 2
        self.damage_bonus = 0


@AttachedAction(Chainsaw)
class ChainsawAttack(MeleeAttack):

    def __init__(self, session: Session, source: Entity, weapon: Chainsaw):
        super().__init__(session, source, weapon)

    async def func(self, source: Entity, target: Entity):
        if percentage_chance(5):
            self.session.say(ls("weapon_chainsaw_jammed").format(source.name))
            self.weapon.WoundUp = False
            self.weapon.turns_active = 0
            self.weapon.reset_stats()
            return

        if not self.weapon.WoundUp:
            self.weapon.reset_stats()
        else:
            self.weapon.cubes = 3
            self.weapon.damage_bonus = 1
            self.weapon.accuracy_bonus = 2
            self.weapon.energy_cost = 2

        source.energy = max(source.energy - self.weapon.energy_cost, 0)

        total_damage = self.calculate_damage(source, target)

        post_damage = await self.publish_post_damage_event(source, target, total_damage)
        target.inbound_dmg.add(source, post_damage, self.session.turn)
        source.outbound_dmg.add(target, post_damage, self.session.turn)

        if not total_damage:
            self.session.say(
                self.MISS_MESSAGE.format(source_name=source.name, attack_text=self.ATTACK_TEXT, target_name=target.name,
                                         weapon_name=self.weapon.name)
            )
        else:
            self.session.say(
                self.ATTACK_MESSAGE.format(attack_emoji=self.ATTACK_EMOJI, source_name=source.name,
                                           attack_text=self.ATTACK_TEXT,
                                           target_name=target.name, weapon_name=self.weapon.name, damage=total_damage)
            )

    async def publish_post_damage_event(self, source: Entity, target: Entity, damage: int) -> int:
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        await self.event_manager.publish(message)
        return message.damage


@AttachedAction(Chainsaw)
class WoundUpChainsaw(FreeWeaponAction):
    id = 'wound_up_chainsaw'
    target_type = OwnOnly()
    priority = -10

    @property
    def hidden(self) -> bool:
        return self.session.turn < self.weapon.cooldown_turn

    @property
    def name(self):
        return ls("weapon_chainsaw_enable_name")

    async def func(self, source, target):
        if self.weapon.WoundUp:
            self.session.say(ls("weapon_chainsaw_active").format(source.name, self.weapon.turns_active))
            return

        self.weapon.WoundUp = True
        self.weapon.turns_active = 5
        self.weapon.cooldown_turn = self.session.turn + 5

        self.session.say(ls("weapon_chainsaw_switch_text").format(source.name))

        @At(self.session.id, turn=self.session.turn + 4, event=PostTickGameEvent)
        async def disable_chainsaw(context: EventContext[PostTickGameEvent]):
            self.weapon.WoundUp = False
            self.weapon.reset_stats()
            context.session.say(ls("weapon_chainsaw_disable_text").format(source.name))


