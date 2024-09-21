import VegansDeluxe.rebuild as rebuild
import VegansDeluxe.deluxe as deluxe

from game.States.Emptiness import Emptiness
from game.States.Weakness import Weakness
from game.States.Hunger import Hunger
from game.States.Dehydration import Dehydration
from game.States.Mutilation import Mutilation
from game.States.CorrosiveMucus import CorrosiveMucus

from game.Skills.ExplosionMagic import ExplosionMagic
from game.Skills.SweetTooth import SweetTooth
from game.Skills.Echo import Echo
from game.Skills.Tactician import Tactician
from game.Skills.Dash import Dash
from game.Skills.Heroism import Heroism
from game.Skills.FinalBlow import FinalBlow
from game.Skills.Toad import Toad
from game.Skills.Invulnerable import Invulnerable

from game.Items.CryoGrenade import CryoGrenade
from game.Items.CaffeineCandy import CaffeineCandy
from game.Items.SourCandy import SourCandy
from game.Items.SweetCandy import SweetCandy
from game.Items.DeathGrenade import DeathGrenade
from game.Items.EnergyGrenade import EnergyGrenade
from game.Items.MucusInTheBottle import MucusInTheBottle

from game.Weapons.AbyssalBlade import AbyssalBlade
from game.Weapons.CursedSword import CursedSword
from game.Weapons.GrenadeLauncher import GrenadeLauncher
from game.Weapons.Boomerang import Boomerang
from game.Weapons.Tomahawk import Tomahawk
from game.Weapons.Shurikens import Shurikens
from game.Weapons.NeedleFan import NeedleFan
from game.Weapons.Emitter import Emitter
from game.Weapons.Chainsaw import Chainsaw
from game.Weapons.Hook import Hook
from game.Weapons.HellBow import HellBow
from game.Weapons.ElectricWhip import ElectricWhip
from game.Weapons.VampiricWhip import VampiricWhip
from game.Weapons.Dagger import Dagger
#from game.Weapons.Halberd import Halberd

all_states = (rebuild.all_states + deluxe.all_items + [Emptiness] + [Weakness, Hunger, Dehydration, Mutilation] +
              [CorrosiveMucus])
all_items = (rebuild.all_items + [CryoGrenade, CaffeineCandy, SourCandy, SweetCandy, DeathGrenade, EnergyGrenade] +
             [MucusInTheBottle]
             )
all_weapons = (
        rebuild.all_weapons + deluxe.all_weapons + [AbyssalBlade, Hook, HellBow, ElectricWhip, Tomahawk] +
        [CursedSword, GrenadeLauncher, Boomerang, Shurikens, NeedleFan, Emitter, Chainsaw, VampiricWhip, Dagger]
)
all_skills = (rebuild.all_skills + deluxe.all_skills + [ExplosionMagic, SweetTooth, Echo, Tactician, Dash, Heroism] +
              [FinalBlow, Toad, Invulnerable]
              )

game_items_pool = rebuild.game_items_pool + [CryoGrenade, EnergyGrenade, MucusInTheBottle]
