import VegansDeluxe.rebuild as rebuild
import VegansDeluxe.deluxe as deluxe

from game.States.Emptiness import Emptiness
from game.States.Weakness import Weakness
from game.States.Hunger import Hunger

from game.Skills.ExplosionMagic import ExplosionMagic

from game.Weapons.AbyssalBlade import AbyssalBlade
from game.Weapons.CursedSword import CursedSword
from game.Weapons.GrenadeLauncher import GrenadeLauncher
from game.Weapons.Boomerang import Boomerang
from game.Weapons.Javelin import Javelin
from game.Weapons.Shurikens import Shurikens
from game.Weapons.NeedleFan import NeedleFan
from game.Weapons.Emitter import Emitter
from game.Weapons.Chainsaw import Chainsaw
from game.Weapons.Hook import Hook
from game.Weapons.HellBow import HellBow
from game.Weapons.ElectricWhip import ElectricWhip


all_states = rebuild.all_states + deluxe.all_items + [Weakness, Emptiness] + [Hunger]
all_items = rebuild.all_items
all_weapons = rebuild.all_weapons + deluxe.all_weapons + [AbyssalBlade, CursedSword, GrenadeLauncher] + [Boomerang, Javelin, Shurikens, NeedleFan, Emitter, Chainsaw] + [Hook, HellBow, ElectricWhip]
all_skills = rebuild.all_skills + deluxe.all_skills + [ExplosionMagic]

game_items_pool = rebuild.game_items_pool
