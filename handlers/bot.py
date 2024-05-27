from typing import Union, Optional, List

from VegansDeluxe.core.Translator.LocalizedString import LocalizedString
from telebot import TeleBot, types, REPLY_MARKUP_TYPES
from telebot.apihelper import ApiTelegramException
import time
import traceback


class ExtendedBot(TeleBot):
    def ssend_message(self, *args, **kwargs):
        try:
            return super().send_message(*args, **kwargs)
        except ApiTelegramException as e:
            print(traceback.format_exc())
            if 'Too Many Requests' in e.description:
                time.sleep(5)
                return self.send_message(*args, **kwargs)
        except:
            pass

    def send_message(
            self, chat_id: Union[int, str], text: Union[str, LocalizedString],
            parse_mode: Optional[str] = None,
            entities: Optional[List[types.MessageEntity]] = None,
            disable_web_page_preview: Optional[bool] = None,  # deprecated, for backward compatibility
            disable_notification: Optional[bool] = None,
            protect_content: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,  # deprecated, for backward compatibility
            allow_sending_without_reply: Optional[bool] = None,  # deprecated, for backward compatibility
            reply_markup: Optional[REPLY_MARKUP_TYPES] = None,
            timeout: Optional[int] = None,
            message_thread_id: Optional[int] = None,
            reply_parameters: Optional[types.ReplyParameters] = None,
            link_preview_options: Optional[types.LinkPreviewOptions] = None, locale_code: str = "") -> types.Message:

        if isinstance(text, LocalizedString):
            text = text.localize(locale_code)

        return super().send_message(chat_id, text, parse_mode, entities, disable_web_page_preview, disable_notification,
                                    protect_content, reply_to_message_id, allow_sending_without_reply, reply_markup,
                                    timeout, message_thread_id, reply_parameters, link_preview_options)

    def reply_to(self, message: types.Message, text: Union[str, LocalizedString], **kwargs) -> types.Message:
        if isinstance(text, LocalizedString):
            text = text.localize(message.from_user.language_code)

        return super().reply_to(message, text, **kwargs)

    def get_deep_link(self, data: str):
        return f"https://t.me/{self.user.username}?start={data}"
