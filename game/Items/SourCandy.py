from VegansDeluxe.core import Item, FreeItem, AttachedAction, ActionTag
from VegansDeluxe.core import OwnOnly, EventContext, PostDamagesGameEvent
from VegansDeluxe.core import RegisterItem, At
from VegansDeluxe.core.Translator.LocalizedString import ls


@RegisterItem
class SourCandy(Item):
    id = 'sour_candy'
    name = ls("item_sour_candy_name")


@AttachedAction(SourCandy)
class SourCandyAction(FreeItem):
    id = 'sour_candy'
    name = ls("item_sour_candy_name")
    target_type = OwnOnly()
    priority = -2

    def __init__(self, *args):
        super().__init__(*args)
        self.tags += [ActionTag.MEDICINE]

    async def func(self, source, target):
        # Увеличиваем максимальную энергию на 1
        target.max_energy += 1
        self.session.say(ls("item_sour_candy_effect").format(target.name, target.max_energy))

        def remove_energy_boost(context: EventContext[PostDamagesGameEvent]):
            # Убираем бонусную энергию после 3 ходов
            target.max_energy = max(target.max_energy - 1, 0)
            self.session.say(ls("item_sour_candy_wear_off").format(target.name, target.max_energy))

        # Планируем снятие бонуса через 3 хода
        At(self.session.id, turn=self.session.turn + 2, event=PostDamagesGameEvent)(remove_energy_boost)

        self.session.say(ls("item_sour_candy_use").format(source.name, target.name))

