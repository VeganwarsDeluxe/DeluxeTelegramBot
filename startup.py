from mongoengine import connect

from config import bot_token, mongo_url
from VegansDeluxe.core import Engine
from handlers.bot import ExtendedBot

bot = ExtendedBot(bot_token, skip_pending=True)

connect(host=mongo_url, db='viro')

engine = Engine()