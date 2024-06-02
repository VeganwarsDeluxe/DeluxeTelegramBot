from VegansDeluxe.rebuild import all_skills, all_weapons, all_items, all_states, game_items_pool

from game.States.Emptiness import Emptiness
from game.States.Weakness import Weakness
from game.Weapons.AbyssalBlade import AbyssalBlade
from game.Weapons.CursedSword import CursedSword
from game.Weapons.GrenadeLauncher import GrenadeLauncher
from game.Weapons.Lance import Lance

all_states += [Weakness, Emptiness]
all_items += []
all_weapons += [AbyssalBlade, CursedSword, GrenadeLauncher]
all_skills += []

game_items_pool += []
