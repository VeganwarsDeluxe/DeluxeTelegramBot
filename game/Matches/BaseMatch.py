import random
from typing import Union

from VegansDeluxe.core.States import State
from VegansDeluxe.core.Translator.LocalizedString import LocalizedString, ls

from VegansDeluxe.core import PreMoveGameEvent, Weapon, Session
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from handlers.callbacks.other import (WeaponInfo, StateInfo, ChooseWeapon, ChooseSkill,
                                      Additional, ActionChoice, TargetChoice, Back)
from game.Entities.TelegramEntity import TelegramEntity
from startup import engine
from utils import KLineMerger, smartsplit

import game.content


class BaseMatch:
    name: str | LocalizedString = ls("matches.basic")

    def __init__(self, chat_id: int, bot: Bot):
        self.bot: Bot = bot

        self.id: str = str(chat_id)
        self.chat_id = chat_id
        self.session: Session[TelegramEntity] = self.create_session(self.id)
        self.locale = ""

        self.lobby_message: Message | None = None
        self.lobby = True

        self.skill_cycles = 2
        self.skill_number = 5

        self.weapon_number = 3

        self.items_given = 2

        self.cowed = False

        self.action_indexes = []

    @property
    def unready_players(self) -> list[TelegramEntity]:
        return [p for p in self.session.entities if not p.ready]

    @property
    def not_chosen_weapon(self) -> list[TelegramEntity]:
        return [p for p in self.session.entities if not p.chose_weapon]

    @property
    def not_chosen_skills(self) -> list[TelegramEntity]:
        return [p for p in self.session.entities if not p.chose_skills]

    @property
    def not_chosen_items(self) -> list[TelegramEntity]:
        return [p for p in self.session.entities if not p.chose_items]

    @property
    def player_ids(self):
        return [p.id for p in self.session.entities]

    def get_player(self, user_id):
        user_id = str(user_id)
        result = [p for p in self.session.entities if p.id == user_id]
        if result:
            return result[0]

    def join_session(self, user_id, user_name) -> TelegramEntity:
        player = TelegramEntity(self.session.id, user_name, user_id)
        player.energy, player.max_energy, player.hp, player.max_hp = 5, 5, 4, 4
        self.session.attach_entity(player)
        engine.attach_states(player, game.content.all_states)
        return player

    def create_session(self, chat_id: str) -> Session[TelegramEntity]:
        session = Session(engine.event_manager)
        session.id = chat_id
        engine.attach_session(session)
        return session

    async def send_end_game_messages(self):
        """Sends messages when the game ends."""
        if list(self.session.alive_entities):
            tts = ls("match_end_winner_team").format(list(self.session.alive_entities)[0].name)
        else:
            tts = ls("match_end_no_winner")
        await self.broadcast_to_players(tts)
        await self.send_message_to_chat(tts)

    def get_target_choice_buttons(self, targets, index: int, player: TelegramEntity):
        code = player.locale

        kb = []

        for target in targets:
            kb.append([
                InlineKeyboardButton(
                    text=self.localize_text(target.name),
                    callback_data=TargetChoice(game_id=self.id, target_id=target.id, index=index).pack(),
                )])
        kb.append([InlineKeyboardButton(
            text=ls('buttons_back').localize(code), callback_data=Back(game_id=self.id).pack()
        )])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)
        return kb

    async def choose_act(self, user_id, target_id, act_id):
        player = self.get_player(user_id)
        target = self.session.get_entity(target_id)
        action = engine.action_manager.get_action(self.session, player, act_id)
        queue = engine.action_manager.queue_action(self.session, player, act_id)
        action.target = target

        if action.type == 'item':
            player.items.remove(action.item)

        if queue:
            await self.send_act_buttons(player)
            return
        player.ready = True
        if not self.unready_players:
            await self.cycle()

    async def broadcast_logs(self):
        await self.send_logs_to_chat(self.session.texts)
        await self.broadcast_logs_to_players(self.session.texts)

    async def send_logs_to_chat(self, logs: list[str, LocalizedString]):
        log = self.localize_logs(logs, self.locale)

        for message in log.split('\n\n'):
            message = self.merge_lines(message)
            for tts in smartsplit.smart_split(message):
                await self.send_message_to_chat(tts)

    async def send_logs_to_player(self, logs: list[str, LocalizedString], player: TelegramEntity):
        code = player.locale
        log = self.localize_logs(logs, code)

        for message in log.split('\n\n'):
            new_message = self.merge_lines(message)
            await self.send_message_to_player(new_message, player)

    async def send_message_to_chat(self, text: Union[str, LocalizedString]):
        text = self.localize_text(text, code=self.locale)

        for tts in smartsplit.smart_split(text):
            try:
                await self.bot.send_message(self.chat_id, tts)
            except Exception as e:
                print(f"Failed to send message to chat {self.chat_id}. Error: {str(e)}")

    async def send_message_to_player(self, text: Union[str, LocalizedString], player: TelegramEntity):
        text = self.localize_text(text, code=player.locale)

        for tts in smartsplit.smart_split(text):
            try:
                # Skip if the player is an NPC or if the game is in DMs
                if player.user_id == self.chat_id or player.npc:
                    return
                await self.bot.send_message(player.user_id, tts)
            except Exception as e:
                print(f"Failed to send message to player {player.user_id}. Error: {str(e)}")

    async def broadcast_logs_to_players(self, logs: list[str, LocalizedString]):
        for player in self.session.entities:
            await self.send_logs_to_player(logs, player)

    async def broadcast_to_players(self, message: Union[str, LocalizedString]):
        """Notifies all players in the game."""
        for player in self.session.entities:
            await self.send_message_to_player(message, player)

    def localize_logs(self, logs: list[str, LocalizedString], code: str = '') -> str:
        return "".join([self.localize_text(log, code) for log in logs])

    def localize_text(self, text: Union[str, LocalizedString], code: str = ''):
        if isinstance(text, LocalizedString):
            text = text.localize(code)
        return text

    def merge_lines(self, text):
        return KLineMerger.merge_lines(text.split("\n"))

    async def send_act_buttons(self, player):
        kb = self.get_act_buttons(player)
        tts = self.get_act_text(player)

        await self.bot.send_message(player.user_id, tts, reply_markup=kb)

    def get_act_text(self, player: TelegramEntity):
        code = player.locale

        tts = (ls("action_info_turn").format(self.session.turn)
               .localize(code) + '\n')
        tts += (ls("action_info_hp").format(player.hearts, player.hp, player.max_hp)
                .localize(code) + '\n')
        tts += (ls("action_info_energy").format(player.energies, player.energy, player.max_energy)
                .localize(code) + '\n')
        tts += (ls("action_info_hit_chance").format(int(player.weapon.hit_chance(player)))
                .localize(code) + "\n") if player.weapon else ''  # TODO: Maybe check for ATTACK tag?

        for notification in player.notifications:
            tts += self.localize_text(notification, code)

        return tts

    async def start_game(self):
        """Starts a game."""
        self.session.start()
        await self.pre_move()

    def update_game_actions(self):
        """Updates actions for a game."""
        engine.action_manager.update_actions(self.session)
        self.action_indexes = []

    def handle_pre_move_events(self):
        """Handles events before a move."""
        self.session.pre_move(), engine.event_manager.publish(PreMoveGameEvent(self.session.id, self.session.turn))

    async def execute_actions(self):
        """Executes actions for all alive entities."""
        for player in self.session.alive_entities:
            if player.get_state('stun').stun:  # TODO: Hardcoded. It can be done better
                engine.action_manager.queue_action(self.session, player, 'lay_stun')
                player.ready = True
                if not self.unready_players:
                    await self.cycle()
            elif player.npc:
                player.choose_act(self.session)
            else:
                await self.send_act_buttons(player)

    def map_buttons(self, player: TelegramEntity):  # TODO: Rethink this function. Maybe we can use action tags here?
        code = player.locale

        engine.action_manager.update_entity_actions(self.session, player)

        buttons = {
            'first_row': [],
            'second_row': [],
            'additional': [],
            'approach_row': [],
            'skip_row': []
        }
        for action in engine.action_manager.get_available_actions(self.session, player):
            name = self.localize_text(action.name, code)
            button = InlineKeyboardButton(text=name,
                                          callback_data=ActionChoice(game_id=self.id, action_id=action.id).pack())
            if action.id in ['attack', 'reload']:
                buttons['first_row'].append(button)
            elif action.id in ['dodge']:
                buttons['second_row'].append(button)
            elif action.id in ['approach']:
                buttons['approach_row'].append(button)
            elif action.id in ['skip', 'extinguish']:
                buttons['skip_row'].append(button)
            else:
                buttons['additional'].append(button)
        return buttons

    def get_act_buttons(self, player):
        code = player.locale

        buttons = self.map_buttons(player)

        kb = []
        buttons['first_row'].reverse()
        buttons['second_row'].append(
            InlineKeyboardButton(text=ls('buttons_info').localize(code), callback_data=StateInfo(state_id='777').pack())
            # TODO: Huh?? 777? Pasyuk much?
        )

        kb.append(buttons['first_row'])
        kb.append(buttons['second_row'])
        kb.append([InlineKeyboardButton(
            text=ls('buttons_additional').localize(code), callback_data=Additional(game_id=self.id).pack())
        ])
        kb.append(buttons['approach_row'])
        kb.append(buttons['skip_row'])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)
        return kb

    def get_additional_buttons(self, player: TelegramEntity):
        code = player.locale

        engine.action_manager.update_entity_actions(self.session, player)

        all_buttons = []
        items = []
        for action in engine.action_manager.get_available_actions(self.session, player):
            name = self.localize_text(action.name, code)
            if action.type == 'item':
                items.append(action)
                continue
            button = InlineKeyboardButton(text=name,
                                          callback_data=ActionChoice(game_id=self.id, action_id=action.id).pack())
            if action.id in ['attack', 'reload', 'approach', 'dodge', 'skip', 'extinguish']:
                pass
            else:
                all_buttons.append(button)

        item_count = {}
        for item_action in items:
            if item_action.item.id not in item_count:
                item_count[item_action.item.id] = 0
            item_count[item_action.item.id] += 1

        item_buttons = []
        added_items = []
        for action in items:
            if action.item.id in added_items:
                continue
            name = f"{self.localize_text(action.name, code)} ({item_count[action.item.id]})"
            button = InlineKeyboardButton(text=name,
                                          callback_data=ActionChoice(game_id=self.id, action_id=action.id).pack())
            item_buttons.append(button)
            added_items.append(action.item.id)

        kb = []
        for button in all_buttons:
            kb.append([button])
        for button in item_buttons:
            kb.append([button])
        kb.append([InlineKeyboardButton(
            text=ls('buttons_back').localize(code), callback_data=Back(game_id=self.id).pack()
        )])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)
        return kb

    async def check_game_status(self):
        """Checks the status of the game and sends end game messages if needed."""
        if not self.session.active:
            await self.send_end_game_messages()
            engine.detach_session(self.session)
            return False
        return True

    async def pre_move(self):
        """Handles pre-move procedures."""
        self.update_game_actions()
        self.handle_pre_move_events()
        if not await self.check_game_status():
            return
        await self.execute_actions()
        if not self.unready_players:
            await self.cycle()

    async def cycle(self):
        if not await self.check_game_status():
            return
        self.session.say(ls('match_turn_number').format(self.session.turn))
        self.session.move()
        await self.broadcast_logs()
        await self.pre_move()

    async def choose_items(self):
        for player in self.not_chosen_items:
            code = player.locale

            given = []
            for _ in range(self.items_given):
                item = random.choice(game.content.game_items_pool)()
                pool = list(filter(lambda i: i.id not in given, game.content.game_items_pool))
                if pool:
                    item = random.choice(pool)()
                given.append(item.id)
                player.items.append(item)
            player.chose_items = True
            if player.npc:
                continue
            items = ", ".join([self.localize_text(item.name, code) for item in player.items])
            await self.send_message_to_player(ls("match_your_items").format(items), player)

    async def choose_weapons(self):
        for player in self.not_chosen_weapon:
            if player.npc:
                continue
            await self.send_weapon_choice_buttons(player)
        if not self.not_chosen_weapon:
            await self.send_message_to_chat(ls("match_weapons_chosen"))
            await self.choose_skills()

    async def choose_skills(self):
        for player in self.not_chosen_skills:
            if player.npc:
                continue
            await self.send_skill_choice_buttons(player)
        if not self.not_chosen_skills:
            weapons_text = '\n' + '\n'.join([f'{player.name}: {self.localize_text(player.weapon.name, self.locale)}'
                                             for player in self.session.alive_entities])
            text = ls('match_start').format(weapons_text)
            await self.send_message_to_chat(text)
            await self.pre_move()

    async def send_weapon_choice_buttons(self, player):
        code = player.locale

        weapons: list[Weapon] = []
        for _ in range(self.weapon_number):
            variants = list(filter(lambda w: w.id not in [w.id for w in weapons], game.content.all_weapons))
            if not variants:
                break
            choice = random.choice(variants)
            weapons.append(choice)

        weapons.sort(key=lambda w: w.id)

        kb = []
        for weapon in weapons:
            kb.append(
                [InlineKeyboardButton(text=self.localize_text(weapon.name, code),
                                      callback_data=ChooseWeapon(game_id=self.id, weapon_id=weapon.id).pack()),
                 InlineKeyboardButton(text=ls('buttons_information').localize(code),
                                      callback_data=WeaponInfo(weapon_id=weapon.id).pack()
                                      )]
            )
        kb.append([InlineKeyboardButton(text=ls("buttons_random_weapon").localize(code),
                                        callback_data=ChooseWeapon(game_id=self.id,
                                                                   weapon_id="random").pack())])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)

        await self.bot.send_message(player.user_id, ls("match_choose_weapon").localize(code), reply_markup=kb)

    async def send_skill_choice_buttons(self, player, cycle=1):
        code = player.locale

        skills: list[State] = []
        for _ in range(self.skill_number):
            variants = list(filter(lambda s: s.id not in [s.id for s in skills], game.content.all_skills))
            variants = list(filter(lambda s: s.id not in [s.id for s in player.states], variants))
            if not variants:
                break
            choice = random.choice(variants)
            skills.append(choice)

        skills.sort(key=lambda s: s.id)

        kb = []
        for skill in skills:
            kb.append([
                InlineKeyboardButton(text=skill.name.localize(),
                                     callback_data=ChooseSkill(cycle=cycle, game_id=self.id, skill_id=skill.id)
                                     .pack()),
                InlineKeyboardButton(text=ls("buttons_information").localize(code),
                                     callback_data=StateInfo(state_id=skill.id).pack())])
        kb.append([InlineKeyboardButton(text=ls("buttons_random_skill").localize(code),
                                        callback_data=ChooseSkill(cycle=cycle, game_id=self.id, skill_id="random")
                                        .pack())])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)

        await self.bot.send_message(player.user_id,
                              ls("match_choose_skill").format(cycle, self.skill_cycles).localize(code),
                              reply_markup=kb)
