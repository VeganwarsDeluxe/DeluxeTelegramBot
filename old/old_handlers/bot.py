from typing import Union, Optional, List

from VegansDeluxe.core.Translator.LocalizedString import LocalizedString
from telebot import TeleBot, types, REPLY_MARKUP_TYPES
from telebot.apihelper import ApiTelegramException
import time
import traceback


class ExtendedBot(TeleBot):
    def get_deep_link(self, data: str):
        return f"https://t.me/{self.user.username}?start={data}"
