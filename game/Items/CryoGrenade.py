from VegansDeluxe.core import AttachedAction, RegisterItem, ActionTag
from VegansDeluxe.core import Entity
from VegansDeluxe.core import Item
from VegansDeluxe.core import DecisiveItem
import random

from VegansDeluxe.core import Session
from VegansDeluxe.core import Enemies
from VegansDeluxe.core.Translator.LocalizedList import LocalizedList
from VegansDeluxe.core.Translator.LocalizedString import ls


@RegisterItem
class CryoGrenade(Item):
    id = 'cryo_grenade'
    name = ls("item_cryo_grenade_name")


@AttachedAction(CryoGrenade)
class CryoGrenadeAction(DecisiveItem):
    id = 'cryo_grenade'
    name = ls("item_cryo_grenade_name")
    target_type = Enemies()

    def __init__(self, session: Session, source: Entity, item: Item):
        super().__init__(session, source, item)
        self.tags += [ActionTag.HARMFUL]
        self.range = 2

    def func(self, source, target):
        targets = []
        for _ in range(self.range):
            target_pool = list(filter(lambda t: t not in targets,
                                      self.get_targets(source, Enemies())
                                      ))
            if not target_pool:
                continue
            target = random.choice(target_pool)
            stun_state = target.get_state('stun')
            stun_state.stun += 2
            targets.append(target)

        source.energy = max(source.energy - 2, 0)
        self.session.say(
            ls("item_cryo_grenade_text")
            .format(source.name, LocalizedList([t.name for t in targets]))
        )

    @property
    def blocked(self):
        return self.source.energy < 2