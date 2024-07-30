import VegansDeluxe.rebuild as rebuild
import VegansDeluxe.deluxe as deluxe

from game.States.Emptiness import Emptiness
from game.States.Weakness import Weakness
from game.Weapons.AbyssalBlade import AbyssalBlade
from game.Weapons.CursedSword import CursedSword
from game.Weapons.GrenadeLauncher import GrenadeLauncher

all_states = rebuild.all_states + deluxe.all_items + [Weakness, Emptiness]
all_items = rebuild.all_items
all_weapons = rebuild.all_weapons + deluxe.all_weapons + [AbyssalBlade, CursedSword, GrenadeLauncher]
all_skills = rebuild.all_skills + deluxe.all_skills

game_items_pool = rebuild.game_items_pool
