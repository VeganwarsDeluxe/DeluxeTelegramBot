from mongoengine import connect

from config import bot_token, mongourl
from VegansDeluxe.core import Engine
from VegansDeluxe.core.ContentManager import content_manager as cm
from deluxe.bot.bot import ExtendedBot
from deluxe.db import RatingManager

bot = ExtendedBot(bot_token, skip_pending=True)
rm = RatingManager()

connect(host=mongourl, db='viro')

engine = Engine()
