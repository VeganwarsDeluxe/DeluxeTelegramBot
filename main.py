import random
import traceback

from telebot.types import Message

import config

import VegansDeluxe
from VegansDeluxe.core import Own, ls
from VegansDeluxe.core.ContentManager import content_manager as cm

from flow.MatchStartFlow import MatchStartFlow
from game.Matches.Matchmaker import Matchmaker
from startup import bot, engine

import game.content

import handlers.matches
from VegansDeluxe.core.Translator.Translator import translator


mm = Matchmaker(bot, engine)
handlers.matches.initialize_module(bot, mm)


@bot.message_handler(commands=['do'])
def vd_prepare_handler(m):
    if m.from_user.id not in config.admin_ids:
        return
    if not m.text.count(' '):
        return
    code = m.text.split(' ', 1)[1]
    try:
        result = eval(code)
    except:
        result = traceback.format_exc()
    bot.reply_to(m, f"Code: {code}\n\nResult: {result}")


@bot.message_handler(commands=['vd_delete'])
def vd_prepare_handler(m):
    match = mm.get_match(m.chat.id)
    if not match:
        bot.reply_to(m, ls("bot.delete.game_not_started"))
        return
    del mm.matches[match.id]
    engine.detach_session(match.session)
    bot.reply_to(m, ls("bot.delete.success"))


@bot.message_handler(commands=['vd_join'])
def vd_join_handler(m: Message):
    match = mm.get_match(m.chat.id)
    if not match:
        bot.reply_to(m, ls("bot.join.game_not_started"))
        return
    if str(m.from_user.id) in match.session.player_ids:
        bot.reply_to(m, ls("bot.join.already_joined"))
        return
    if not match.lobby:
        bot.reply_to(m, ls("bot.join.game_already_started"))
        return
    try:
        bot.send_message(m.from_user.id, ls("bot.join.success"),
                         locale_code=m.from_user.language_code)
    except:
        bot.reply_to(m, ls("bot.join.open_pm"))
        return
    match.join_session(m.from_user.id, m.from_user.full_name)

    bot.send_message(m.chat.id, ls("bot.join.text").format(m.from_user.full_name),
                     locale_code=m.from_user.language_code)


@bot.message_handler(commands=['start'], func=lambda m: " jg_" in m.text)
def vd_prepare_handler(m):
    game_id = int(m.text.split('_')[-1])
    match = mm.get_match(game_id)

    if not match:
        bot.reply_to(m, ls("bot.callback.join.game_not_started"))
        return
    if str(m.from_user.id) in match.session.player_ids:
        bot.reply_to(m, ls("bot.join.already_joined"))
        return
    if not match.lobby:
        bot.reply_to(m, ls("bot.join.game_already_started"))
        return
    match.join_session(m.from_user.id, m.from_user.full_name)

    bot.send_message(m.from_user.id, ls("bot.join.success"), locale_code=m.from_user.language_code)
    bot.send_message(m.chat.id, ls("bot.join.text").format(m.from_user.full_name),
                     locale_code=m.from_user.language_code)


@bot.message_handler(commands=['vd_go'])
def vd_join_handler(m):
    msf = MatchStartFlow(m.chat.id, m.from_user.id, mm)
    result = msf.execute()
    bot.reply_to(m, result) if result else None


@bot.callback_query_handler(func=lambda c: c.data == 'vd_go')
def act_callback_handler(c):
    msf = MatchStartFlow(c.message.chat.id, c.from_user.id, mm)
    result = msf.execute()
    bot.answer_callback_query(c.id, result) if result else None


@bot.message_handler(commands=['vd_suicide'])
def vd_join_handler(m):
    match = mm.get_match(m.chat.id)
    if not match:
        return
    player = match.session.get_player(m.from_user.id)
    if not player:
        return
    if match.lobby:
        return
    player.dead = True
    player.hp = 0
    if not match.session.unready_players:
        match.session.say(ls("bot.suicide.text").format(player.name))
        match.cycle()


@bot.callback_query_handler(func=lambda c: c.data.startswith('cw'))
def act_callback_handler(c):
    _, game_id, weapon_id = c.data.split('_', 2)
    match = mm.get_match(game_id)
    if not match:
        bot.edit_message_text(ls("bot.cw.game_is_finished").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    if match.lobby:
        bot.edit_message_text(ls("bow.cw.do_not_hurry").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    player = match.session.get_player(c.from_user.id)
    if not player:
        bot.edit_message_text(ls("bot.cw.not_in_game").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    if player.chose_weapon:
        bot.edit_message_text(ls("bot.cw.stop_doing_that").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    if weapon_id == 'random':
        weapon = random.choice(game.content.all_weapons)(game_id, player.id)
    else:
        weapon = cm.get_weapon(weapon_id)(game_id, player.id)
    player.weapon = weapon
    player.chose_weapon = True
    if not match.session.not_chosen_weapon:
        bot.send_message(match.session.chat_id, ls("bot.cw.weapons_chosen"), locale_code=match.locale)
        match.choose_skills()

    bot.edit_message_text(ls("bot.cw.weapon_chosen").format(weapon.name).localize(c.from_user.language_code),
                          c.message.chat.id, c.message.message_id)


@bot.callback_query_handler(func=lambda c: c.data.startswith('cs'))
def act_callback_handler(c):
    _, cycle, game_id, skill_id = c.data.split('_', 3)
    match = mm.get_match(int(game_id))
    if not match:
        bot.edit_message_text(ls("bot.cw.game_is_finished").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    if match.lobby:
        bot.edit_message_text(ls("bow.cw.do_not_hurry").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    player = match.session.get_player(c.from_user.id)
    if not player:
        bot.edit_message_text(ls("bot.cw.not_in_game").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    if player.chose_skills or player.skill_cycle == int(cycle):
        bot.edit_message_text(ls("bot.cw.stop_doing_that").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    skill = cm.get_state(skill_id)
    if skill_id == 'random':
        variants = list(filter(lambda s: s.id not in [s.id for s in player.states], game.content.all_skills))
        if not variants:
            variants = game.content.all_skills
        skill = random.choice(variants)
    engine.attach_states(player, [skill])
    player.skill_cycle = int(cycle)

    if int(cycle) >= match.skill_cycles:
        player.chose_skills = True
    else:
        match.send_skill_choice_buttons(player, int(cycle) + 1)

    bot.edit_message_text(ls("bot.cs.skill_chosen").format(skill.name),
                          c.message.chat.id, c.message.message_id)

    if not match.session.not_chosen_skills:
        tts = ls("bot.common.game_is_starting").localize(match.locale)
        for player in match.session.alive_entities:
            tts += f'\n{player.name}: {player.weapon.name}'
        bot.send_message(match.session.chat_id, tts)
        match.start_game()


@bot.callback_query_handler(func=lambda c: c.data.startswith('ci'))
def act_callback_handler(c):
    _, skill_id = c.data.split('_', 3)
    bot.answer_callback_query(c.id, cm.get_state(skill_id).description, show_alert=True)


@bot.callback_query_handler(func=lambda c: c.data.startswith('wi'))
def act_callback_handler(c):
    _, weapon_id = c.data.split('_', 3)
    bot.answer_callback_query(c.id, cm.get_weapon(weapon_id).description, show_alert=True)


@bot.callback_query_handler(func=lambda c: c.data.startswith('act_'))
def act_callback_handler(c):
    _, game_id, act_id = c.data.split('_', 2)
    match = mm.get_match(game_id)
    if not match:
        bot.edit_message_text('Игра стухла!',
                              c.message.chat.id, c.message.message_id)
        return
    player = match.session.get_player(c.from_user.id)
    if not player:
        bot.edit_message_text(ls("bot.error.player_not_found").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    action = engine.action_manager.get_action(match.session, player, act_id)
    if not action:
        bot.edit_message_text('Кнопка стухла!',
                              c.message.chat.id, c.message.message_id)
        return
    if action.blocked:
        bot.answer_callback_query(c.id, "Кнопка заблокирована!", show_alert=True)
        return

    target = player
    if not action.target_type.own == Own.SELF_ONLY:
        match.action_indexes.append(action)
        index = len(match.action_indexes) - 1
        kb = match.choose_target(action.targets, index)
        bot.edit_message_text('Выбор цели:', c.message.chat.id, c.message.message_id, reply_markup=kb)
        return

    bot.edit_message_text(f"Выбрано: {action.name} на {action.target.name}", c.message.chat.id, c.message.message_id)
    match.choose_act(c.from_user.id, target.id, act_id)


@bot.callback_query_handler(func=lambda c: c.data.startswith('tgt_'))
def act_callback_handler(c):
    _, game_id, target_id, index = c.data.split('_', 3)
    match = mm.get_match(game_id)
    if not match:
        bot.edit_message_text('Игра стухла!', c.message.chat.id, c.message.message_id)
        return
    player = match.session.get_player(c.from_user.id)
    if not player:
        bot.edit_message_text(ls("bot.error.player_not_found").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    target = match.session.get_player(target_id)
    if not target:
        bot.edit_message_text('Игрок стух!', c.message.chat.id, c.message.message_id)
        return
    if len(match.action_indexes) < int(index) + 1:
        bot.edit_message_text('Все стухло!', c.message.chat.id, c.message.message_id)
        return
    action = match.action_indexes[int(index)]
    action.target = target
    bot.edit_message_text(f"Выбрано: {action.name} на {action.target.name}", c.message.chat.id, c.message.message_id)
    match.choose_act(c.from_user.id, target.id, action.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith('back_'))
def act_callback_handler(c):
    _, game_id = c.data.split('_', 1)
    match = mm.get_match(game_id)
    if not match:
        bot.edit_message_text('Игра стухла!', c.message.chat.id, c.message.message_id)
        return
    player = match.session.get_player(c.from_user.id)
    if not player:
        bot.edit_message_text(ls("bot.error.player_not_found").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    kb = match.get_act_buttons(player)
    tts = match.get_act_text(player)
    bot.edit_message_text(tts, c.message.chat.id, c.message.message_id, reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith('more_'))
def act_callback_handler(c):
    _, game_id = c.data.split('_', 1)
    match = mm.get_match(game_id)
    if not match:
        bot.edit_message_text('Игра стухла!', c.message.chat.id, c.message.message_id)
        return
    player = match.session.get_player(c.from_user.id)
    if not player:
        bot.edit_message_text(ls("bot.error.player_not_found").localize(c.from_user.language_code),
                              c.message.chat.id, c.message.message_id)
        return
    kb = match.get_additional_buttons(player)
    bot.edit_message_text('Дополнительно:', c.message.chat.id, c.message.message_id, reply_markup=kb)


bot.send_message(config.boot_chat, f"♻️Core: `{VegansDeluxe.core.__version__}`\n"
                                   f"🤖Latest bot patch: ```"
                                   f"\n - fixed /vd_delete"
                                   f"```",
                 parse_mode="Markdown")
bot.infinity_polling()
