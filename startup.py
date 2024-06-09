from mongoengine import connect

from config import bot_token, mongo_url, default_locale
from VegansDeluxe.core import Engine, translator

from game.Matches.Matchmaker import Matchmaker
from old.old_handlers.bot import ExtendedBot

bot = ExtendedBot(bot_token, skip_pending=True)

connect(host=mongo_url, db='viro')

translator.load_folder("localizations")
translator.load_folder("game/localizations")

translator.default_locale = default_locale
engine = Engine()
mm = Matchmaker(engine)

with open("version.txt", 'r') as file:
    version = file.read()
