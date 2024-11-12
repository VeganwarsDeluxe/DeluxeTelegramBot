from VegansDeluxe.core import Engine, translator

from config import default_locale
from game.Matches.Matchmaker import Matchmaker

translator.load_folder("localizations")
translator.load_folder("game/localizations")

translator.default_locale = default_locale
engine = Engine()
mm = Matchmaker(engine)

with open("version.txt", 'r') as file:
    version = file.read()
