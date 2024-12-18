import random
from typing import Union

from VegansDeluxe.core import PreMoveGameEvent, Weapon, Session, ActionTag, EventContext, RegisterEvent, Engine
from VegansDeluxe.core.Question.Question import Question
from VegansDeluxe.core.Question.QuestionEvents import QuestionGameEvent
from VegansDeluxe.core.States import State
from VegansDeluxe.core.Translator.LocalizedString import LocalizedString, ls
from VegansDeluxe.rebuild import Stun
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

import game.content
from db import db
from game.Entities.TelegramEntity import TelegramEntity
from handlers.callbacks.other import (WeaponInfo, StateInfo, ChooseWeapon, ChooseSkill,
                                      Additional, ActionChoice, TargetChoice, Back, AnswerChoice, JoinTeam,
                                      RefreshTeamList, LeaveTeam)
from utils import KLineMerger, smartsplit


class BaseMatch:
    name: str | LocalizedString = ls("matches.basic")

    def __init__(self, chat_id: int, bot: Bot, engine: Engine):
        self.bot: Bot = bot
        self.engine: Engine = engine

        self.id: str = str(chat_id)
        self.session: Session = Session(engine.event_manager)
        self.chat_id = chat_id
        self.locale = ""

        self.lobby_message: Message | None = None
        self.lobby = True

        self.skill_cycles = 2
        self.skill_number = 5

        self.weapon_number = 3

        self.item_choice_pool = game.content.game_items_pool
        self.items_given = 2

        self.cowed = False

        self.action_indexes = []

        self.detached = False  # TODO: Temporary fix. Figure out why are we detaching session for every entity.

        # TODO: Worst decision ever. Please find normal solution. We are becoming Rebuild.
        #  At least we have typehints!
        self.question_cache: dict[str, Question] = {}

    async def init_async(self):
        self.session: Session[TelegramEntity] = await self.create_session(self.id)

        @RegisterEvent(self.session.id, QuestionGameEvent, subscription_id="question_handler")
        async def handling_question(context: EventContext[QuestionGameEvent]):
            """
            Event handler.
            If there's a Question event, sends a keyboard to the player.
            """
            player = self.get_player(context.event.entity_id)
            if player.npc:
                # TODO: But really. NPCs also might wanna answer. Maybe something like NPC.choose_act()?
                return

            text = self.localize_text(context.event.question.text, player.locale)
            question = context.event.question
            self.question_cache.update({question.id: question})

            kb = []
            for choice in question.choices:
                kb.append([
                    InlineKeyboardButton(
                        text=self.localize_text(choice.text, player.locale),
                        callback_data=
                        AnswerChoice(game_id=self.id, question_id=question.id, choice_id=choice.id).pack()
                    )]
                )
            kb = InlineKeyboardMarkup(inline_keyboard=kb)

            await self.bot.send_message(player.user_id, text, reply_markup=kb)

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

    async def join_session(self, user_id: int, user_name) -> TelegramEntity:
        code = db.get_user_locale(user_id)

        player = TelegramEntity(self.session.id, user_name, user_id, code)
        player.energy, player.max_energy, player.hp, player.max_hp = 5, 5, 4, 4
        self.session.attach_entity(player)
        await self.engine.attach_states(player, game.content.all_states)
        await self.send_team_selection_menu(player)
        return player

    async def create_session(self, chat_id: str) -> Session[TelegramEntity]:
        session = Session(self.engine.event_manager)
        session.id = chat_id
        await self.engine.attach_session(session)
        return session

    async def send_end_game_messages(self):
        """Sends messages when the game ends."""
        if list(self.session.alive_entities):
            tts = ls("deluxe.matches.messages.end_winner_team").format(list(self.session.alive_entities)[0].name)
        else:
            tts = ls("deluxe.matches.messages.end_no_winner")
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
            text=ls("deluxe.buttons.back").localize(code), callback_data=Back(game_id=self.id).pack()
        )])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)
        return kb

    async def choose_act(self, user_id, target_id, act_id):
        player = self.get_player(user_id)
        target = self.session.get_entity(target_id)
        action = self.engine.action_manager.get_action(self.session, player, act_id)

        # TODO: Wired AI training here. Please rework, refactor.
        # try:
        #    choice_index = engine.action_manager.get_available_actions(self.session, player).index(action)
        #    training_data = battle_ai.compile_training_data(self.session, player, choice_index=choice_index)
        #    await battle_ai.train([training_data])
        #    battle_ai.save()
        # except:
        #    pass

        action.target = target

        if action.type == 'item':
            player.items.remove(action.item)

        if action.cost == -1:
            queue = True
            await action.execute()
        else:
            queue = self.engine.action_manager.queue_action_instance(action)

        await self.engine.action_manager.update_actions(self.session)

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
                if self.chat_id == 0:
                    print(f"[TG]: {text}")
                    continue
                await self.bot.send_message(self.chat_id, tts)
            except Exception as e:
                print(f"Failed to send message to chat {self.chat_id}. Error: {str(e)}")

    async def send_message_to_player(self, text: Union[str, LocalizedString], player: TelegramEntity,
                                     ignore_dm_game: bool = False):
        text = self.localize_text(text, code=player.locale)

        for tts in smartsplit.smart_split(text):
            try:
                # Skip if the player is an NPC or if the game is in DMs
                if (not ignore_dm_game and self.chat_id == player.user_id) or player.npc:
                    return
                await self.bot.send_message(player.user_id, tts)
            except Exception as e:
                print(f"Failed to send message to player {player.user_id}. Error: {str(e)}")

    async def broadcast_logs_to_players(self, logs: list[str, LocalizedString]):
        for player in self.session.entities:
            if player.npc:
                continue
            await self.send_logs_to_player(logs, player)

    async def broadcast_to_players(self, message: Union[str, LocalizedString]):
        """Notifies all players in the game."""
        for player in self.session.entities:
            if player.npc:
                continue
            await self.send_message_to_player(message, player)

    def localize_logs(self, logs: list[str, LocalizedString], code: str = '') -> str:
        return "".join([self.localize_text(log, code) for log in logs])

    def localize_text(self, text: Union[str, LocalizedString], code: str = ''):
        if not code:
            code = self.locale
        if isinstance(text, LocalizedString):
            text = text.localize(code)
        return text

    def merge_lines(self, text):
        return KLineMerger.merge_lines(text.split("\n"))

    async def send_act_buttons(self, player):
        kb = await self.get_act_buttons(player)
        tts = self.get_act_text(player)

        await self.bot.send_message(player.user_id, tts, reply_markup=kb)

    def get_act_text(self, player: TelegramEntity):
        code = player.locale

        tts = (ls("action.info.turn").format(self.session.turn)
               .localize(code) + '\n')
        tts += (ls("action.info.hp").format(player.hearts, player.hp, player.max_hp)
                .localize(code) + '\n')
        tts += (ls("action.info.energy").format(player.energies, player.energy, player.max_energy)
                .localize(code) + '\n')
        tts += (ls("action.info.hit_chance").format(int(player.weapon.hit_chance(player)))
                .localize(code) + "\n") if player.weapon else ''  # TODO: Maybe check for ATTACK tag?

        for notification in player.notifications:
            tts += self.localize_text(notification, code)

        return tts

    async def start_game(self):
        """Starts a game."""
        await self.session.start()
        await self.pre_move()

    async def update_game_actions(self):
        """Updates actions for a game."""
        await self.engine.action_manager.update_actions(self.session)
        self.action_indexes = []

    async def handle_pre_move_events(self):
        """Handles events before a move."""
        self.session.pre_move()
        await self.engine.event_manager.publish(PreMoveGameEvent(self.session.id, self.session.turn))

    async def execute_actions(self):
        """Executes actions for all alive entities."""
        for entity in self.session.alive_entities:
            entity: TelegramEntity
            if entity.get_state(Stun).stun:  # TODO: Hardcoded. It can be done better
                self.engine.action_manager.queue_action(self.session, entity, 'lay_stun')
                entity.ready = True
                if not self.unready_players:
                    await self.cycle()
                    return
                continue
            if entity.npc:
                await entity.choose_act(self.session)
            else:
                await self.send_act_buttons(entity)

    def get_info_for_player(self, player: TelegramEntity):
        # TODO: Incomplete.
        #  I forgot what it is for already. Info button?
        code = player.locale

        text = f"{self.localize_text(player.name)}\n"
        text += f""

    async def map_buttons(self, player: TelegramEntity):
        code = player.locale

        await self.engine.action_manager.update_entity_actions(self.session, player)

        buttons = {
            'first_row': [],
            'second_row': [],
            'additional': [],
            'approach_row': [],
            'skip_row': []
        }

        for action in self.engine.action_manager.get_available_actions(self.session, player):
            action_name = self.localize_text(action.name, code)
            action_selection = ActionChoice(game_id=self.id, action_id=action.id).pack()
            button = InlineKeyboardButton(text=action_name, callback_data=action_selection)

            if ActionTag.ATTACK in action.tags or ActionTag.RELOAD in action.tags:
                buttons['first_row'].append(button)
            elif action.id in ['dodge']:
                buttons['second_row'].append(button)
            elif action.id in ['approach']:
                buttons['approach_row'].append(button)
            elif action.id in ['skip', 'extinguish'] or ActionTag.SKIP in action.tags:
                buttons['skip_row'].append(button)
            else:
                buttons['additional'].append(button)
        return buttons

    async def get_act_buttons(self, player):
        code = player.locale

        buttons = await self.map_buttons(player)

        kb = []
        buttons['first_row'].reverse()
        buttons['second_row'].append(
            InlineKeyboardButton(text=ls("deluxe.buttons.info").localize(code),
                                 callback_data=StateInfo(state_id='0').pack())
            # TODO: Huh?? 777? Pasyuk much?
            #  This is actually about info. We can combine answerless questions to finally write Visor and info button.
        )

        kb.append(buttons['first_row'])
        kb.append(buttons['second_row'])
        kb.append([InlineKeyboardButton(
            text=ls("deluxe.buttons.additional").localize(code), callback_data=Additional(game_id=self.id).pack())
        ])
        kb.append(buttons['approach_row'])
        kb.append(buttons['skip_row'])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)
        return kb

    async def get_additional_buttons(self, player: TelegramEntity):
        code = player.locale

        await self.engine.action_manager.update_entity_actions(self.session, player)

        all_buttons = []
        items = []
        for action in self.engine.action_manager.get_available_actions(self.session, player):
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
            text=ls("deluxe.buttons.back").localize(code), callback_data=Back(game_id=self.id).pack()
        )])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)
        return kb

    async def check_game_status(self):
        """Checks the status of the game and sends end game messages if needed."""
        if not self.session.active:
            if self.detached:
                # TODO: As i remember, this is a bad bugfix.
                #  This function tries to detach the session multiple times. Which it shouldn't.
                return
            self.detached = True

            await self.send_end_game_messages()
            self.engine.detach_session(self.session)
            return False
        return True

    async def pre_move(self):
        """Handles pre-move procedures."""
        await self.update_game_actions()
        await self.handle_pre_move_events()
        if not await self.check_game_status():
            return
        await self.execute_actions()
        if not self.unready_players:
            await self.cycle()

    async def cycle(self):
        if not await self.check_game_status():
            return
        self.session.say(ls("deluxe.matches.messages.turn_number").format(self.session.turn))
        await self.session.move()
        await self.broadcast_logs()
        await self.pre_move()

    async def choose_items(self):
        for player in self.not_chosen_items:
            code = player.locale

            given = []
            for _ in range(self.items_given):
                item = random.choice(self.item_choice_pool)()
                pool = list(filter(lambda i: i.id not in given, self.item_choice_pool))
                if pool:
                    item = random.choice(pool)()
                given.append(item.id)
                player.items.append(item)
            player.chose_items = True

            items = ", ".join([self.localize_text(item.name, code) for item in player.items])
            await self.send_message_to_player(ls("deluxe.matches.messages.your_items").format(items), player,
                                              ignore_dm_game=True)

    async def choose_weapons(self):
        for player in self.not_chosen_weapon:
            if player.npc:
                continue
            await self.send_weapon_choice_buttons(player)
        if not self.not_chosen_weapon:
            await self.send_message_to_chat(ls("deluxe.matches.messages.weapons_chosen"))
            await self.choose_skills()

    async def choose_skills(self):
        for player in self.not_chosen_skills:
            if player.npc:
                # TODO: But again. Maybe they also should choose skills like any other?
                continue
            if self.skill_cycles == 0:
                player.chose_skills = True
                continue
            await self.send_skill_choice_buttons(player)
        if not self.not_chosen_skills:
            weapons_text = '\n' + '\n'.join([f'{player.name}: {self.localize_text(player.weapon.name, self.locale)}'
                                             for player in self.session.alive_entities])
            text = ls("deluxe.matches.messages.start").format(weapons_text)
            await self.broadcast_to_players(text)
            await self.send_message_to_chat(text)
            await self.pre_move()

    async def announce_team_positions(self):
        await self.send_message_to_chat(self.format_team_list(self.locale)[0])

    def form_team_lists(self) -> dict[int, list[TelegramEntity]]:
        teams = {}
        team_index = 0

        for team in self.session.alive_teams:
            if team:
                team_index += 1
                teams.update({team_index: self.session.get_team(team)})
            else:
                for entity in self.session.get_team(team):
                    team_index += 1
                    teams.update({team_index: [entity]})
        return teams

    def format_team_list(self, code: str = ""):
        tts = ls("bot.teams.team_list").localize(code)
        teams = self.form_team_lists()

        for team_index, team in teams.items():
            player_names = [self.localize_text(entity.name, code) for entity in team]
            player_name = ", ".join(player_names)

            tts += ls("bot.teams.team_info").format(team_index, player_name).localize(code)
        return tts, teams

    async def send_team_selection_menu(self, player):
        tts, kb = self.form_team_selection_menu(player.locale, bool(player.team))
        await self.bot.send_message(player.user_id, tts, reply_markup=kb)

    def form_team_selection_menu(self, code: str = "", show_leave_button=True):
        tts, teams = self.format_team_list(code)

        kb = []
        for team_index, team in teams.items():
            team_id, team_type = f"{team[0].team}", "t"
            if not team[0].team:
                team_id, team_type = f"{team[0].id}", "p"

            kb.append([
                InlineKeyboardButton(text=ls("bot.teams.join_button").format(team_index, len(team)).localize(code),
                                     callback_data=JoinTeam(game_id=self.id,
                                                            team_id=team_id,
                                                            team_type=team_type).pack())
            ])

        kb.append([
            InlineKeyboardButton(text=ls("bot.teams.refresh_button").localize(code),
                                 callback_data=RefreshTeamList(game_id=self.id).pack())
        ])

        if show_leave_button:
            kb.append([
                InlineKeyboardButton(text=ls("bot.teams.leave_button").localize(code),
                                     callback_data=LeaveTeam(game_id=self.id).pack())
            ])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)
        return tts, kb

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
                 InlineKeyboardButton(text=ls("deluxe.buttons.information").localize(code),
                                      callback_data=WeaponInfo(weapon_id=weapon.id).pack()
                                      )]
            )
        kb.append([InlineKeyboardButton(text=ls("deluxe.buttons.random_weapon").localize(code),
                                        callback_data=ChooseWeapon(game_id=self.id,
                                                                   weapon_id="random").pack())])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)

        await self.bot.send_message(player.user_id, ls("deluxe.matches.messages.choose_weapon").localize(code),
                                    reply_markup=kb)

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
                InlineKeyboardButton(text=self.localize_text(skill.name, code),
                                     callback_data=ChooseSkill(cycle=cycle, game_id=self.id, skill_id=skill.id)
                                     .pack()),
                InlineKeyboardButton(text=ls("deluxe.buttons.information").localize(code),
                                     callback_data=StateInfo(state_id=skill.id).pack())])
        kb.append([InlineKeyboardButton(text=ls("deluxe.buttons.random_skill").localize(code),
                                        callback_data=ChooseSkill(cycle=cycle, game_id=self.id, skill_id="random")
                                        .pack())])

        kb = InlineKeyboardMarkup(inline_keyboard=kb)

        await self.bot.send_message(player.user_id,
                                    ls("deluxe.matches.messages.choose_skill").format(cycle,
                                                                                      self.skill_cycles).localize(code),
                                    reply_markup=kb)
