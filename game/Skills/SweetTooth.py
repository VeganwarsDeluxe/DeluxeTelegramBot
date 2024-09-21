from VegansDeluxe.core import RegisterState
from VegansDeluxe.core import StateContext
from VegansDeluxe.core import Session
from VegansDeluxe.core.Skills.Skill import Skill
from VegansDeluxe.core.Translator.LocalizedString import ls
from game.Items.SweetCandy import SweetCandy
from game.Items.SourCandy import SourCandy
from game.Items.CaffeineCandy import CaffeineCandy


class SweetTooth(Skill):
    id = 'sweet_tooth'
    name = ls("skill_sweet_tooth_name")
    description = ls("skill_sweet_tooth_description")


@RegisterState(SweetTooth)
def register(root_context: StateContext[SweetTooth]):
    session: Session = root_context.session
    source = root_context.entity

    source.items.append(SweetCandy())
    source.items.append(SourCandy())
    source.items.append(CaffeineCandy())