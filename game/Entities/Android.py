import random

from VegansDeluxe import rebuild
from VegansDeluxe.core import AttachedAction, Session, ls, percentage_chance, Action
from VegansDeluxe.core.Actions.EntityActions import ReloadAction
from VegansDeluxe.rebuild import Bleeding, ZombieState, Stun, DroppedWeapon, ThrowingKnife, Berserk, \
    Knockdown, Grenade, Molotov, Aflame, Rifle, Ninja, Chitin, FlashGrenade, GasMask, Stimulator, Armor, \
    Flamethrower, Jet
from VegansDeluxe.rebuild.Items.Adrenaline import AdrenalineAction, Adrenaline
from VegansDeluxe.rebuild.Items.FlashGrenade import FlashGrenadeAction
from VegansDeluxe.rebuild.Items.Grenade import GrenadeAction
from VegansDeluxe.rebuild.Items.Jet import JetAction
from VegansDeluxe.rebuild.Items.Molotov import MolotovAction
from VegansDeluxe.rebuild.Items.RageSerum import RageSerumAction
from VegansDeluxe.rebuild.Items.Shield import ShieldAction
from VegansDeluxe.rebuild.Items.Stimulator import StimulatorAction
from VegansDeluxe.rebuild.Items.ThrowingKnife import ThrowingKnifeAction
from VegansDeluxe.rebuild.Skills.Inquisitor import Pray
from VegansDeluxe.rebuild.Skills.ShieldGen import ShieldGenAction
from VegansDeluxe.rebuild.States.Dodge import DodgeAction
from VegansDeluxe.rebuild.States.DroppedWeapon import PickUp
from VegansDeluxe.rebuild.States.KnockDown import StandUp
from VegansDeluxe.rebuild.Weapons.Bow import FireArrow
from VegansDeluxe.rebuild.Weapons.Chain import KnockWeapon
from VegansDeluxe.rebuild.Weapons.Molot import TrueStrike
from VegansDeluxe.rebuild.Weapons.Shaft import KnockDown
from VegansDeluxe.rebuild.Weapons.Sledgehammer import SledgehammerCrush
from VegansDeluxe.rebuild.Weapons.Spear import CounterAttack

from startup import engine
from .NPC import NPC
from .TelegramEntity import TelegramEntity, ApproachAction, SkipTurnAction
from ..Skills.Dash import Dash, DashAction
from ..Skills.ExplosionMagic import Explosion


class Android(NPC):
    weapon_pool = rebuild.all_weapons
    item_pool = rebuild.game_items_pool
    skill_pool = rebuild.all_skills

    def __init__(self, session_id: str, name=ls("🤖|Android")):
        # TODO: Localization
        super().__init__(session_id, name)

        self.weapon = self.choose_weapon()
        self.items.extend(self.choose_items())

        self.hp = 4
        self.max_hp = 5
        self.max_energy = 5

        self.team = 'android'

    def choose_weapon(self):
        return random.choice(self.weapon_pool)(self.session_id, self.id)

    def choose_skills(self):
        pool = self.skill_pool.copy()
        random.shuffle(pool)

        return pool[:2]

    def choose_items(self):
        pool = self.item_pool.copy()
        random.shuffle(pool)

        return pool[0](), pool[1]()

    def can_entity_attack_me(self, target: TelegramEntity, session) -> bool:
        return self in engine.action_manager.get_action(session, target, "attack").targets

    def can_i_attack_entity(self, target: TelegramEntity, session) -> bool:
        # TODO: Detect attacks.
        return target in engine.action_manager.get_action(session, self, "attack").targets

    def targeted_action(self, action_id: str, session: Session[TelegramEntity],
                        target: TelegramEntity | None = None):
        action = engine.action_manager.get_action(session, self, action_id)
        if not action.targets:
            action.target = action.source
        elif not target:
            action.target = random.choice(action.targets)
        else:
            action.target = target
        return action

    async def choose_act(self, session: Session[TelegramEntity]):
        await super().choose_act(session)

        hit_chance = self.hit_chance
        base_hit_chance = hit_chance

        acts = []
        dopitems = []
        enemies = []
        enemies_close = []
        enemies_can_attack_me = []
        enemies_i_can_attack = []
        enemies_zombie = []
        enemies_stunned = []
        enemies_hitin = []
        enemies_lostweapon = []

        lowest_health = 100
        highest_health = -1

        near_death = self.hp == 1 or (self.hp == 2 and self.get_state(Bleeding).bleeding == 1)
        next_turn_death = self.hp == 1 and self.get_state(Bleeding).bleeding == 1

        debuff = 0

        can_regen = not (debuff >= self.max_energy - self.energy)

        for entity in session.entities:
            target = entity
            if not self.is_ally(target) and not target.dead:
                if target not in enemies:
                    enemies.append(target)
                if target in self.nearby_entities:
                    enemies_close.append(target)
                if self.can_entity_attack_me(target, session):
                    enemies_can_attack_me.append(target)
                if self.can_i_attack_entity(target, session):
                    enemies_i_can_attack.append(target)

                if target.get_state(ZombieState).active > 0:
                    enemies_zombie.append(target)
                if target.get_state(Stun).stun > 0:
                    enemies_stunned.append(target)
                if target.get_state(Armor).armor_sum > 0:
                    enemies_hitin.append(target)
                if target.hp < lowest_health:
                    lowest_health = target.hp
                if target.hp > highest_health:
                    highest_health = target.hp
                if target.get_state(DroppedWeapon).weapon:
                    enemies_lostweapon.append(target)

        # Skipping if no enemies.
        if len(enemies) == 0:
            engine.action_manager.queue_action(session, self, SkipTurnAction.id)
            return

        # Considering using a throwing knife if no attacks can take place.
        if len(enemies_can_attack_me) == 0 and len(enemies_i_can_attack) == 0:
            if self.get_item(ThrowingKnife.id):
                acts.append(self.targeted_action(ThrowingKnifeAction.id, session))

        # Considering throwing a knife on first turn with 50% chance.
        if self.get_item(ThrowingKnife.id) and percentage_chance(50) and session.turn == 1:
            acts.append(self.targeted_action(ThrowingKnifeAction.id, session))

        can_attack = bool(enemies_i_can_attack)

        hitins = []
        for entity in session.entities:
            if entity.get_state(Armor).armor_sum > 0 and entity in enemies_i_can_attack:
                hitins.append(entity)

        low = False
        for entity in enemies_i_can_attack:
            if entity.energy <= self.energy or self.energy == self.max_energy or entity not in enemies_can_attack_me:
                low = True
        if self.get_state(Berserk) and self.hp == 1:
            low = True
        if self.get_item(ThrowingKnife.id) and percentage_chance(50) and (
                self.energy >= 4 or self.energy == self.max_energy):
            acts.append(self.targeted_action(ThrowingKnifeAction.id, session))
        if not low:
            hit_chance -= 40
        if len(hitins) == len(enemies_i_can_attack):
            hit_chance -= 50
        if base_hit_chance < 70:
            hit_chance -= 20
        if base_hit_chance < 60:
            hit_chance -= 20
        if len(enemies_i_can_attack) == len(enemies_zombie):
            hit_chance -= 100
        if self.get_state(DroppedWeapon).weapon:
            hit_chance -= 100
            acts.append(self.targeted_action(PickUp.id, session))
        if self.get_state(Knockdown).active:
            hit_chance -= 100
        if percentage_chance(hit_chance) and can_attack:
            # TODO: Fix it or I'll go insane.
            acts.append(self.targeted_action("attack", session))
        else:
            if self.energy >= 2:
                if self.get_item(Grenade.id) and percentage_chance(50) and not self.get_state(Knockdown).active:
                    acts.append(self.targeted_action(GrenadeAction.id, session))
                if self.get_item(Molotov.id):
                    molotov = True
                    for entity in enemies:
                        if entity.get_state(Aflame).timer > 1:
                            molotov = False
                    if molotov and percentage_chance(50) and not self.get_state(Knockdown).active:
                        acts.append(self.targeted_action(MolotovAction.id, session))
                if self.get_item(ThrowingKnife.id) and self.energy >= 4:
                    if (len(enemies) != len(enemies_zombie)
                            and percentage_chance(50) and not self.get_state(Knockdown).active):
                        acts.append(self.targeted_action(ThrowingKnifeAction.id, session))
            if self.energy <= 3 and self.energy < self.max_energy and can_regen:
                acts.append(self.targeted_action(ReloadAction.id, session))
        if self.energy == 0:
            reload_action = self.targeted_action(ReloadAction.id, session)
            if reload_action not in acts and can_regen:
                acts.append(self.targeted_action(ReloadAction.id, session))
            if self.get_item(Adrenaline.id):
                if len(enemies_i_can_attack) != len(enemies_zombie) and percentage_chance(50):
                    if debuff <= 1 and not self.get_state(Knockdown).active:
                        dopitems.append(self.targeted_action(AdrenalineAction.id, session, self))

        flashtargets = []
        for entity in enemies:
            target = entity
            targethitchance = target.hit_chance
            if target.weapon.id == Rifle.id:
                target_weapon: Rifle = target.weapon
                if target.energy > 0:
                    targethitchance += (target_weapon.main_target[1] * 50)
            if target.get_state(Stun).stun > 0 or target.get_state(Knockdown).active:
                targethitchance = 0
            perekatchance = targethitchance - 30
            shieldchance = targethitchance - 30
            flashchance = targethitchance - 30
            hypnotistchance = targethitchance - 30
            counterattackchance = targethitchance
            molitvachance = 0
            if near_death:
                molitvachance += targethitchance
            if self.get_state(Knockdown).active and near_death and targethitchance > 50:
                shieldchance += 40
                flashchance += 40
                hypnotistchance += 40
            if targethitchance > 98 and not self.get_state(Ninja):
                perekatchance = 0
            if targethitchance < 70:
                if not near_death:
                    shieldchance = 0
                    flashchance = 0
                    perekatchance = 0
                    counterattackchance = 0
                else:
                    if targethitchance < 50:
                        shieldchance = 0
                        flashchance = 0
                        perekatchance = 0
                        counterattackchance = 0
            if target.get_state(Aflame).timer > 1 and target.get_state(Aflame).flame > 1:
                perekatchance = 0
                shieldchance = 0
                flashchance = 0
                counterattackchance = 0
                molitvachance = 0
            if self.get_state(Armor).armor_sum > 0:
                perekatchance = 0
                shieldchance = 0
                flashchance = 0
                counterattackchance = 0
                molitvachance = 0
            if target.energy < 4:
                flashchance = 0
            if len(enemies_can_attack_me) == 0:
                perekatchance = 0
                shieldchance = 0
                flashchance = 0
                counterattackchance = 0
                molitvachance = 0
            if len(enemies_lostweapon) == len(enemies_can_attack_me):
                perekatchance = 0
                shieldchance = 0
                flashchance = 0
                hypnotistchance = 0
                molitvachance = 0
            if target in enemies_zombie and target.energy > 1:
                perekatchance = 100
                shieldchance = 100
                flashchance = 100
                counterattackchance = 100
                if near_death:
                    molitvachance = 100
            if self.get_state(ZombieState).active:
                perekatchance = 0
                shieldchance = 0
                flashchance = 0
                counterattackchance = 0
                molitvachance = 0
            if len(enemies_stunned) == len(enemies_can_attack_me):
                perekatchance = 0
                shieldchance = 0
                flashchance = 0
                molitvachance = 0
            if self.get_state(Knockdown).active:
                perekatchance = 0
                counterattackchance = 0

            if percentage_chance(perekatchance):
                if engine.action_manager.is_action_available(session, self, DodgeAction.id):
                    acts.append(self.targeted_action(DodgeAction.id, session, self))
            if percentage_chance(shieldchance):
                if engine.action_manager.is_action_available(session, self, ShieldGenAction.id):
                    acts.append(self.targeted_action(ShieldGenAction.id, session, self))
                elif engine.action_manager.is_action_available(session, self, ShieldAction.id):
                    acts.append(self.targeted_action(ShieldAction.id, session, self))
                elif (self.get_item(Chitin.id) and self.targeted_action(DodgeAction.id, session) not in acts
                      and percentage_chance(60)):
                    dopitems.append(self.targeted_action(Chitin.id, session, self))
            if percentage_chance(counterattackchance):
                if engine.action_manager.is_action_available(session, self, CounterAttack.id):
                    if base_hit_chance >= 70 and percentage_chance(base_hit_chance):
                        acts.append(self.targeted_action(CounterAttack.id, session))
            if percentage_chance(molitvachance) and engine.action_manager.is_action_available(session, self, Pray.id):
                acts.append(self.targeted_action(Pray.id, session, self))
            if percentage_chance(flashchance):
                if self.get_item(FlashGrenade.id):
                    if target in enemies_can_attack_me:
                        if not target.get_state(GasMask):
                            acts.append(self.targeted_action(FlashGrenadeAction.id, session))
                            flashtargets.append(target)
            if target.hp == 1:
                if self.get_item(Adrenaline.id) and self.energy <= 3:
                    if debuff <= 1:
                        dopitems.append(self.targeted_action(AdrenalineAction.id, session, self))

        if len(enemies) != len(enemies_close) and not self.weapon.ranged:
            if (len(enemies_can_attack_me) == 0 and len(enemies_i_can_attack) == 0
                    and self.energy < self.max_energy and can_regen):
                acts.append(self.targeted_action(ReloadAction.id, session))
            else:
                if not engine.action_manager.is_action_available(session, self, Dash.id):
                    if not enemies_i_can_attack:
                        acts.append(self.targeted_action(ApproachAction.id, session))
        if self.get_item(Stimulator.id) and (self.max_hp - self.hp) >= 2 and percentage_chance(80):
            if len(enemies_stunned) != len(enemies):
                acts.append(self.targeted_action(StimulatorAction.id, session, self))

        if self.get_state(Aflame).timer > 1 > self.get_state(Armor).armor_sum:
            if (not self.get_state(ZombieState).active
                    and self.targeted_action(Chitin.id, session, self) not in dopitems):
                acts.append(self.targeted_action(SkipTurnAction.id, session))
                dodge = self.targeted_action(DodgeAction.id, session)
                if dodge in acts:
                    acts.remove(dodge)
                flash_grenade_act = self.targeted_action(FlashGrenadeAction.id, session)
                if flash_grenade_act in acts:
                    acts.remove(flash_grenade_act)

        if not acts:
            if self.energy <= 2 and self.energy < self.max_energy:
                if can_regen:
                    acts.append(self.targeted_action(ReloadAction.id, session))
                else:
                    if self.energy > 0:
                        # TODO: Fix it or !!
                        acts.append(self.targeted_action("attack", session))
                    else:
                        acts.append(self.targeted_action(SkipTurnAction.id, session))
                        print("Skipping 5")
            else:
                # TODO: Fix it or !!
                acts.append(self.targeted_action("attack", session))

        if (self.get_state(Aflame).timer > 1 > self.get_state(Armor).armor_sum
                and self.targeted_action(Chitin.id, session, self) not in dopitems
                and not self.get_state(ZombieState).active):
            acts = [self.targeted_action(SkipTurnAction.id, session)]
            print("Skipping 4")

        # CHOICE SELECTION
        act: Action = random.choice(acts)

        if not self.get_state(ZombieState).active:
            if next_turn_death and self.get_item(Stimulator.id):
                act = self.targeted_action(StimulatorAction.id, session, self)
        if self.get_state(ZombieState).active:
            if self.get_item(Chitin.id) and self.targeted_action(Chitin.id, session, self) not in dopitems:
                dopitems.append(self.targeted_action(Chitin.id, session, self))
            if self.get_state(ZombieState).timer >= 1:
                if self.energy > 0:
                    if len(enemies_i_can_attack) > 0:
                        # TODO: Fix it or !!
                        act = self.targeted_action("attack", session)
                if self.get_item(Adrenaline.id) and debuff <= 1:
                    if len(enemies_i_can_attack) > 0:
                        dopitems.append(self.targeted_action(AdrenalineAction.id, session, self))
                elif self.get_item(ThrowingKnife.id):
                    act = self.targeted_action(ThrowingKnifeAction.id, session)
                if engine.action_manager.is_action_available(session, self, GrenadeAction.id):
                    act = self.targeted_action(GrenadeAction.id, session)
            else:
                if base_hit_chance < 50:
                    if self.energy < self.max_energy and can_regen:
                        act = self.targeted_action(ReloadAction.id, session, self)
                    else:
                        if len(enemies_i_can_attack) > 0:
                            # TODO: Fix it or !!
                            act = self.targeted_action("attack", session)
                if 65 >= base_hit_chance >= 50:
                    if percentage_chance(base_hit_chance):
                        if len(enemies_i_can_attack) > 0:
                            # TODO: Fix it or !!
                            act = self.targeted_action("attack", session)
                    else:
                        if self.energy < self.max_energy and can_regen:
                            act = self.targeted_action(ReloadAction.id, session, self)
                        else:
                            if len(enemies_i_can_attack) > 0:
                                # TODO: Fix it or !!
                                act = self.targeted_action("attack", session)
                if base_hit_chance > 65:
                    if len(enemies_i_can_attack) > 0:
                        # TODO: Fix it or !!
                        act = self.targeted_action("attack", session)
                if (self.get_state(Aflame).timer > 1
                        and self.get_state(Aflame).flame > 2
                        and self.weapon.id == Flamethrower.id):
                    if self.energy > 1:
                        act = self.targeted_action(SkipTurnAction.id, session)
                        print("Skipping 3")
                    else:
                        if can_regen:
                            act = self.targeted_action(ReloadAction.id, session, self)

        # TODO: Fix it or !!
        charge = False
        if act == self.targeted_action("attack", session):
            if self.hp >= 1 and self.get_item(Grenade.id) and self.energy >= 2 and percentage_chance(40):
                act = self.targeted_action(GrenadeAction.id, session)
            if engine.action_manager.is_action_available(session, self, DashAction.id):
                charge = True

            targets = []
            if len(enemies_zombie) == len(enemies_i_can_attack):
                for entity in enemies_i_can_attack:
                    targets.append(entity)
                    if entity.hp == lowest_health:
                        targets.append(entity)
            elif len(hitins) == len(enemies_i_can_attack):
                for entity in enemies_i_can_attack:
                    if entity not in enemies_zombie:
                        targets.append(entity)
                        if entity.hp == lowest_health:
                            targets.append(entity)
            else:
                for entity in enemies_i_can_attack:
                    if entity.get_state(Armor).armor_sum < 1 and entity not in enemies_zombie:
                        targets.append(entity)
                        if entity.hp == lowest_health:
                            targets.append(entity)
            if not targets:
                if self.energy < self.max_energy:
                    act = self.targeted_action(ReloadAction.id, session)
                else:
                    act = self.targeted_action(SkipTurnAction.id, session)
                    print("Skipping 2")
            else:
                target = random.choice(targets)
                if not self.get_state(Knockdown).active:
                    act = self.targeted_action("attack", session, target)
                else:
                    act = self.targeted_action(StandUp.id, session)
                if (engine.action_manager.is_action_available(session, self, KnockWeapon.id)
                        and percentage_chance(70) and target.energy < target.max_energy):
                    if not self.get_state(Knockdown).active:
                        act = self.targeted_action(KnockWeapon.id, session, target)
                    else:
                        act = self.targeted_action(StandUp.id, session)
                if engine.action_manager.is_action_available(session, self, FireArrow.id) and percentage_chance(40):
                    if not self.get_state(Knockdown).active:
                        act = self.targeted_action(FireArrow.id, session, target)
                    else:
                        act = self.targeted_action(StandUp.id, session)
                if engine.action_manager.is_action_available(session, self, KnockDown.id) and percentage_chance(40):
                    if not self.get_state(Knockdown).active:
                        act = self.targeted_action(KnockDown.id, session, target)
                    else:
                        act = self.targeted_action(StandUp.id, session)
                if (engine.action_manager.is_action_available(session, self, TrueStrike.id)
                        and self.energy >= 4 and percentage_chance(50)):
                    if not self.get_state(Knockdown).active:
                        act = self.targeted_action(TrueStrike.id, session, target)
                    else:
                        act = self.targeted_action(StandUp.id, session)
                kuvalda = False
                if (engine.action_manager.is_action_available(session, self, SledgehammerCrush.id)
                        and self.energy >= 4 and target.energy > 1):
                    kuvalda = True
                if kuvalda and percentage_chance(50):
                    if not self.get_state(Knockdown).active:
                        act = self.targeted_action(SledgehammerCrush.id, session, target)
                    else:
                        act = self.targeted_action(StandUp.id, session)
                if charge:
                    if not self.get_state(Knockdown).active:
                        act = self.targeted_action(DashAction.id, session, target)
                    else:
                        act = self.targeted_action(StandUp.id, session)

        elif act.id == ReloadAction.id:
            if self.get_state(Knockdown).active:
                act = self.targeted_action(StandUp.id, session)
            else:
                if self.get_item(Jet.id) and percentage_chance(50):
                    dopitems.append(self.targeted_action(JetAction.id, session, self))
                elif (engine.action_manager.is_action_available(session, self, RageSerumAction.id) and
                      percentage_chance(30)):
                    dopitems.append(self.targeted_action(RageSerumAction.id, session, self))
        elif act.id in [GrenadeAction.id, MolotovAction.id] and self.get_state(Knockdown).active:
            act = self.targeted_action(StandUp.id, session)
        elif act.id == DodgeAction.id:
            if self.get_state(Knockdown).active:
                if engine.action_manager.is_action_available(session, self, ShieldGenAction.id):
                    act = self.targeted_action(ShieldGenAction.id, session, self)
                elif engine.action_manager.is_action_available(session, self, ShieldAction.id):
                    act = self.targeted_action(ShieldAction.id, session, self)
                else:
                    act = self.targeted_action(StandUp.id, session)
        if next_turn_death:
            if engine.action_manager.is_action_available(session, self, Pray.id):
                act = self.targeted_action(Pray.id, session, self)
                dopitems = []

        for entity in enemies:
            target = entity
            if engine.action_manager.is_action_available(session, target, Explosion.id):
                if engine.action_manager.is_action_available(session, self, ShieldGenAction.id):
                    act = self.targeted_action(ShieldGenAction.id, session, self)
                elif engine.action_manager.is_action_available(session, self, ShieldAction.id):
                    act = self.targeted_action(ShieldAction.id, session, self)
                elif (engine.action_manager.is_action_available(session, self, SledgehammerCrush.id)
                      and self.energy >= 4 and not self.get_state(Knockdown).active):
                    act = self.targeted_action(SledgehammerCrush.id, session, target)
                else:
                    act = self.targeted_action(SkipTurnAction.id, session)
                    print("Skipping 1")

        if not act:
            session.say("🐭| 😭🍵.")
            act = self.targeted_action(SkipTurnAction.id, session)
        for item in dopitems:
            if item.item not in self.items:
                continue
            engine.action_manager.queue_action_instance(item)
            if item.type == 'item':
                self.items.remove(item.item)
        engine.action_manager.queue_action_instance(act)
        if act.type == 'item' and act.item in self.items:
            self.items.remove(act.item)

    async def choose_act_old(self, session: Session[TelegramEntity]):
        await super().choose_act(session)

        dodge_available = engine.action_manager.is_action_available(session, self, DodgeAction.id)
        stimulator_available = engine.action_manager.is_action_available(session, self, rebuild.Stimulator.id)
        shield_available = (engine.action_manager.is_action_available(session, self, rebuild.Shield.id)
                            or engine.action_manager.is_action_available(session, self, ShieldGenAction.id))

        defence_action_available = (dodge_available or shield_available)

        # Check if able to heal.
        if self.hp <= 2 and stimulator_available:
            stimulator_action = engine.action_manager.get_action(session, self, rebuild.Stimulator.id)
            self.items.remove(stimulator_action.item)
            engine.action_manager.queue_action_instance(stimulator_action)
            return

        choice_pool = []

        attack_action = engine.action_manager.get_action(session, self, "attack")
        if not attack_action.targets:
            act = engine.action_manager.get_action(session, self, ApproachAction.id)
            act.target = self
            choice_pool.append(act)
        elif self.hit_chance >= 60:
            attack_action.target = random.choice(attack_action.targets)
            choice_pool.append(attack_action)

        if self.hit_chance < 60:
            reload_action = engine.action_manager.get_action(session, self, ReloadAction.id)
            choice_pool.append(reload_action)

        if choice_pool:
            engine.action_manager.queue_action_instance(random.choice(choice_pool))
            return

        session.say("🤖|The android stands still.")


@AttachedAction(Android)
class ApproachAction(ApproachAction):
    pass


@AttachedAction(Android)
class ReloadAction(ReloadAction):
    pass


@AttachedAction(Android)
class SkipTurnAction(SkipTurnAction):
    pass
