import DeluxeMod.content
from DeluxeMod.Skills.Echo import Echo
from DeluxeMod.Skills.ExplosionMagic import ExplosionMagic
from DeluxeMod.Skills.Heroism import Heroism
from DeluxeMod.Skills.Tactician import Tactician
from DeluxeMod.Weapons.Tomahawk import Tomahawk
from VegansDeluxe.core import ls
from VegansDeluxe.rebuild import Necromancer, Visor

from Matches.BaseMatch import BaseMatch


class TournierMatch(BaseMatch):
    name = ls("matches.tournier")

    def __init__(self, chat_id, bot, engine):
        super().__init__(chat_id, bot, engine)

        self.skill_choice_pool = DeluxeMod.content.all_skills.copy()
        self.skill_choice_pool.remove(ExplosionMagic)
        self.skill_choice_pool.remove(Heroism)
        self.skill_choice_pool.remove(Necromancer)
        self.skill_choice_pool.remove(Tactician)
        self.skill_choice_pool.remove(Visor)
        self.skill_choice_pool.remove(Echo)

        self.weapon_choice_pool = DeluxeMod.content.all_weapons.copy()
        self.weapon_choice_pool.remove(Tomahawk)
