from VegansDeluxe.core import EventContext
from VegansDeluxe.core import PostActionsGameEvent, At
from VegansDeluxe.core import PostDamageGameEvent
from VegansDeluxe.core import RangedAttack, RegisterWeapon, Entity, AttachedAction
from VegansDeluxe.core.Session import Session
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon


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
        self.current_needles = 1
        self.max_needles = 10


@AttachedAction(NeedleFan)
class NeedleFanAttack(RangedAttack):

    def __init__(self, session: Session, source: Entity, weapon: NeedleFan):
        super().__init__(session, source, weapon)
        self.register_event_handlers()

    async def func(self, source: Entity, target: Entity):
        if self.weapon.current_needles > 0:
            used_needles = self.weapon.current_needles
            total_damage = (self.calculate_damage(source, target) * used_needles)

            source.energy = max(source.energy - self.weapon.energy_cost, 0)

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

                self.weapon.current_needles = 0

    async def publish_post_damage_event(self, source: Entity, target: Entity, damage: int) -> int:
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        await self.event_manager.publish(message)
        return message.damage

    def register_event_handlers(self):
        @At(self.session.id, turn=self.session.turn, event=PostActionsGameEvent)
        async def handle_needle_recovery(context: EventContext[PostActionsGameEvent]):
            self.recovery_needles()

    def recovery_needles(self):
        if self.weapon.current_needles < self.weapon.max_needles:
            self.weapon.current_needles += 1
