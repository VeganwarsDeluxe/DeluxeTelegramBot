from VegansDeluxe.core import Item, FreeItem, AttachedAction, ActionTag
from VegansDeluxe.core import OwnOnly, EventContext, PostDamagesGameEvent
from VegansDeluxe.core import RegisterItem, At
from VegansDeluxe.core.Translator.LocalizedString import ls


@RegisterItem
class CaffeineCandy(Item):
    id = 'caffeine_candy'
    name = ls("item_caffeine_candy_name")


@AttachedAction(CaffeineCandy)
class CaffeineCandyAction(FreeItem):
    id = 'caffeine_candy'
    name = ls("item_caffeine_candy_name")
    target_type = OwnOnly()
    priority = -2

    def __init__(self, *args):
        super().__init__(*args)
        self.tags += [ActionTag.MEDICINE]

    async def func(self, source, target):
        def apply_energy_boost(context: EventContext[PostDamagesGameEvent]):
            energy_recovered = min(1, source.max_energy - source.energy)
            source.energy += energy_recovered
            self.session.say(ls("item_caffeine_candy_effect").format(target.name, target.energy))

        # Запланировать увеличение энергии на 3 следующих хода
        for turn_offset in range(0, 3):
            At(self.session.id, turn=self.session.turn + turn_offset, event=PostDamagesGameEvent)(apply_energy_boost)

        self.session.say(ls("item_caffeine_candy_use").format(source.name, target.name))