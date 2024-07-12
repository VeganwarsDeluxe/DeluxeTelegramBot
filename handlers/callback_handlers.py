import random

from VegansDeluxe.core import ls, Own
from VegansDeluxe.core.ContentManager import content_manager as cm
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.formatting import Text

from handlers.callbacks.other import (WeaponInfo, StateInfo, ChooseWeapon, ChooseSkill, StartGame,
                                      Additional, ActionChoice, TargetChoice, Back)
from flow.MatchStartFlow import MatchStartFlow
from startup import mm, engine
import game.content

r = Router()


@r.callback_query(WeaponInfo.filter())
async def echo_handler(query: CallbackQuery, callback_data: WeaponInfo) -> None:
    code = ""  # TODO: PASS CODE HERE
    response = cm.get_weapon(callback_data.weapon_id).description.localize(code)

    await query.answer(response, show_alert=True)


@r.callback_query(StateInfo.filter())
async def echo_handler(query: CallbackQuery, callback_data: StateInfo) -> None:
    code = ""  # TODO: PASS CODE HERE
    response = cm.get_state(callback_data.state_id).description.localize(code)

    await query.answer(response, show_alert=True)


@r.callback_query(ChooseWeapon.filter())
async def echo_handler(query: CallbackQuery, callback_data: ChooseWeapon) -> None:
    code = ""  # TODO: PASS CODE HERE
    bot = query.bot

    match = mm.get_match(callback_data.game_id)
    if not match:
        await bot.edit_message_text(ls("bot.cw.game_is_finished").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    if match.lobby:
        await bot.edit_message_text(ls("bow.cw.do_not_hurry").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    player = match.get_player(query.from_user.id)
    if not player:
        await bot.edit_message_text(ls("bot.cw.not_in_game").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    if player.chose_weapon:
        await bot.edit_message_text(ls("bot.cw.stop_doing_that").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    if callback_data.weapon_id == 'random':
        weapon = random.choice(game.content.all_weapons)(callback_data.game_id, player.id)
    else:
        weapon = cm.get_weapon(callback_data.weapon_id)(callback_data.game_id, player.id)
    player.weapon = weapon
    player.chose_weapon = True
    if not match.not_chosen_weapon:
        await bot.send_message(match.chat_id, ls("bot.cw.weapons_chosen").localize(match.locale))
        await match.choose_skills()

    await bot.edit_message_text(ls("bot.cw.weapon_chosen").format(weapon.name).localize(code),
                                query.message.chat.id, query.message.message_id)


@r.callback_query(ChooseSkill.filter())
async def h(query: CallbackQuery, callback_data: ChooseSkill) -> None:
    code = ""  # TODO: PASS CODE HERE
    bot = query.bot

    match = mm.get_match(int(callback_data.game_id))
    if not match:
        await bot.edit_message_text(ls("bot.cw.game_is_finished").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    if match.lobby:
        await bot.edit_message_text(ls("bow.cw.do_not_hurry").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    player = match.get_player(query.from_user.id)
    if not player:
        await bot.edit_message_text(ls("bot.cw.not_in_game").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    if player.chose_skills or player.skill_cycle == callback_data.cycle:
        await bot.edit_message_text(ls("bot.cw.stop_doing_that").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    skill = cm.get_state(callback_data.skill_id)
    if callback_data.skill_id == 'random':
        variants = list(filter(lambda s: s.id not in [s.id for s in player.states], game.content.all_skills))
        if not variants:
            variants = game.content.all_skills
        skill = random.choice(variants)
    engine.attach_states(player, [skill])
    player.skill_cycle = callback_data.cycle

    if callback_data.cycle >= match.skill_cycles:
        player.chose_skills = True
    else:
        await match.send_skill_choice_buttons(player, callback_data.cycle + 1)

    await bot.edit_message_text(ls("bot.cs.skill_chosen").format(skill.name).localize(code),
                                chat_id=query.message.chat.id, message_id=query.message.message_id)

    if not match.not_chosen_skills:
        tts = ls("bot.common.game_is_starting").localize(match.locale)
        for player in match.session.alive_entities:
            tts += f'\n{player.name}: {player.weapon.name}'
        await bot.send_message(match.chat_id, tts)
        await match.start_game()


@r.callback_query(Additional.filter())
async def h(query: CallbackQuery, callback_data: Additional) -> None:
    code = ""  # TODO: PASS CODE HERE
    bot = query.bot

    match = mm.get_match(callback_data.game_id)
    if not match:
        await bot.edit_message_text(ls("bot.error.game_not_found").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    player = match.get_player(query.from_user.id)
    if not player:
        await bot.edit_message_text(ls("bot.error.player_not_found").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    kb = match.get_additional_buttons(player)
    await bot.edit_message_text(ls("bot.common.additional").localize(code),
                                query.message.chat.id, query.message.message_id, reply_markup=kb)


@r.callback_query(ActionChoice.filter())
async def h(query: CallbackQuery, callback_data: ActionChoice) -> None:
    code = ""  # TODO: PASS CODE HERE
    bot = query.bot

    match = mm.get_match(callback_data.game_id)
    if not match:
        await bot.edit_message_text(ls("bot.error.game_not_found").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    player = match.get_player(query.from_user.id)
    if not player:
        await bot.edit_message_text(ls("bot.error.player_not_found").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    action = engine.action_manager.get_action(match.session, player, callback_data.action_id)
    if not action:
        await bot.edit_message_text(ls("bot.error.invalid_button").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    if action.blocked:
        await bot.answer_callback_query(query.id, ls("bot.common.button_is_blocked").localize(code), show_alert=True)
        return

    target = player
    if not action.target_type.own == Own.SELF_ONLY:
        match.action_indexes.append(action)
        index = len(match.action_indexes) - 1
        kb = match.get_target_choice_buttons(action.targets, index, player)
        await bot.edit_message_text(ls("bot.common.target_choice").localize(code),
                                    query.message.chat.id, query.message.message_id, reply_markup=kb)
        return

    await bot.edit_message_text(ls("bot.common.chosen_action").format(action.name, action.target.name).localize(code),
                                query.message.chat.id, query.message.message_id)
    await match.choose_act(query.from_user.id, target.id, callback_data.action_id)


@r.callback_query(TargetChoice.filter())
async def h(query: CallbackQuery, callback_data: TargetChoice) -> None:
    code = ""  # TODO: PASS CODE HERE
    bot = query.bot

    match = mm.get_match(callback_data.game_id)
    if not match:
        await bot.edit_message_text(ls("bot.error.game_not_found").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    player = match.get_player(query.from_user.id)
    if not player:
        await bot.edit_message_text(ls("bot.error.player_not_found").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    target = match.get_player(callback_data.target_id)
    if not target:
        await bot.edit_message_text(ls("bot.error.player_not_found").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    if len(match.action_indexes) < callback_data.index + 1:
        await bot.edit_message_text(ls("bot.error.invalid_button").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    action = match.action_indexes[callback_data.index]
    action.target = target
    await bot.edit_message_text(
        ls("bot.common.chosen_action").format(action.name, action.target.name).localize(code),
        query.message.chat.id, query.message.message_id)
    await match.choose_act(query.from_user.id, target.id, action.id)


@r.callback_query(Back.filter())
async def h(query: CallbackQuery, callback_data: Back) -> None:
    code = ""  # TODO: PASS CODE HERE
    bot = query.bot

    match = mm.get_match(callback_data.game_id)
    if not match:
        await bot.edit_message_text(ls("bot.error.game_not_found").localize(code), query.message.chat.id,
                                    query.message.message_id)
        return
    player = match.get_player(query.from_user.id)
    if not player:
        await bot.edit_message_text(ls("bot.error.player_not_found").localize(code),
                                    query.message.chat.id, query.message.message_id)
        return
    kb = match.get_act_buttons(player)
    tts = match.get_act_text(player)
    await bot.edit_message_text(tts, query.message.chat.id, query.message.message_id, reply_markup=kb)


@r.callback_query(StartGame.filter())
async def h(query: CallbackQuery):
    code = ''  # TODO: PASS CODE HERE

    msf = MatchStartFlow(query.message.chat.id, query.from_user.id, mm)
    result = await msf.execute()
    if result:
        await query.message.reply(**Text(result.localize(code)).as_kwargs())
