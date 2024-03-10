from mongoengine import connect

from config import bot_token, mongourl
from VegansDeluxe.core import Engine
from bot.bot import ExtendedBot
from db import RatingManager

bot = ExtendedBot(bot_token, skip_pending=True)
rm = RatingManager()

connect(host=mongourl, db='viro')

engine = Engine()
