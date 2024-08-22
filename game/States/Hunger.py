from VegansDeluxe.core.Actions.StateAction import DecisiveStateAction
from VegansDeluxe.core import AttachedAction
from VegansDeluxe.core import RegisterState, RegisterEvent
from VegansDeluxe.core import StateContext, EventContext
from VegansDeluxe.core import PostUpdatesGameEvent, PostDamagesGameEvent, PostTickGameEvent
from VegansDeluxe.core import Session
from VegansDeluxe.core import State
from VegansDeluxe.core.Translator.LocalizedString import ls

class Hunger(State):
    id = 'hunger'

    def __init__(self):
        super().__init__()
        self.hunger = 0

@RegisterState(Hunger)
def register(root_context: StateContext[Hunger]):
    session: Session = root_context.session
    source = root_context.entity
    state = root_context.state

    @RegisterEvent(session.id, event=PostUpdatesGameEvent)
    def apply_hunger_effects(context: EventContext[PostUpdatesGameEvent]):
        if state.hunger >= 1:
            accuracy_penalty = 1

            if state.hunger >= 4:
                accuracy_penalty = 1
                max_damage_penalty = 1

            if state.hunger >= 6:
                accuracy_penalty = 2
                min_damage_penalty = 1
                max_damage_penalty = 1
                max_energy_penalty = 1

            for action in context.action_manager.get_actions(session, source):
                if hasattr(action, 'accuracy'):
                    action.accuracy -= accuracy_penalty
                if hasattr(action, 'max_damage'):
                    action.max_damage -= max_damage_penalty
                if hasattr(action, 'min_damage'):
                    action.min_damage -= min_damage_penalty
                if hasattr(action, 'max_energy'):
                    action.max_energy -= max_energy_penalty

    @RegisterState(Hunger)
    def register(root_context: StateContext[Hunger]):
        session: Session = root_context.session
        source = root_context.entity
        state = root_context.state

        @RegisterEvent(session.id, event=PostTickGameEvent)
        def skip_turn(context: EventContext[PostTickGameEvent]):
            if state.hunger > 0:
                state.hunger -= 5
                if state.hunger < 0:
                    state.hunger = 0

        @RegisterEvent(session.id, event=PostUpdatesGameEvent)
        def use_items(context: EventContext[PostUpdatesGameEvent]):
            hunger_reducing_items = {'adrenaline', 'jet', 'chitin', 'rage-serum', 'stimulator'}

            for item in list(source.inventory):
                if item.id in hunger_reducing_items:
                    if state.hunger >= 3:
                        state.hunger -= 3
                    else:
                        state.hunger = 0
                    session.say(ls("hunger_reduced_by_item").format(source.name, item.name, state.hunger))
                    source.inventory.remove(item)
