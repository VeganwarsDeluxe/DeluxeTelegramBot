from mongoengine import connect

from config import mongo_url, default_locale
from VegansDeluxe.core import Engine, translator

from game.Matches.Matchmaker import Matchmaker

connect(host=mongo_url, db='viro')

translator.load_folder("localizations")
translator.load_folder("game/localizations")

translator.default_locale = default_locale
engine = Engine()
mm = Matchmaker(engine)

with open("version.txt", 'r') as file:
    version = file.read()
