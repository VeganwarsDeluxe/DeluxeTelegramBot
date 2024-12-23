from VegansDeluxe.core import Engine, translator

from Matches.Matchmaker import Matchmaker
from config import default_locale

translator.load_folder("localizations")

translator.default_locale = default_locale
engine = Engine()
mm = Matchmaker(engine)

with open("version.txt", 'r') as file:
    version = file.read()
