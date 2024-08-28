from VegansDeluxe.core import Item, FreeItem, AttachedAction, ActionTag
from VegansDeluxe.core import RegisterItem, At
from VegansDeluxe.core import OwnOnly, EventContext, PostDamagesGameEvent
from VegansDeluxe.core.Translator.LocalizedString import ls

from game.States.Regeneration import Regeneration  # Исправление на правильное имя состояния

@RegisterItem
class SweetCandy(Item):
    id = 'sweet_candy'
    name = ls("item_sweet_candy_name")


@AttachedAction(SweetCandy)
class SweetCandyAction(FreeItem):
    id = 'sweet_candy'
    name = ls("item_sweet_candy_name")
    target_type = OwnOnly()
    priority = -2

    def __init__(self, *args):
        super().__init__(*args)
        self.tags += [ActionTag.MEDICINE]

    def func(self, source, target):
        # Retrieve the current state
        regeneration = target.get_state('regeneration')

        if regeneration:
            # If the state exists, modify it
            if regeneration.active:
                regeneration.regeneration -= 1
            regeneration.active = True
        else:
            # If the state does not exist, create and attach it
            regeneration = Regeneration()
            regeneration.active = True
            regeneration.regeneration = 3
            target.attach_state(regeneration, self.session.event_manager)

        # Notify the session about the effect
        self.session.say(ls("sweet_candy_effect").format(source.name))
