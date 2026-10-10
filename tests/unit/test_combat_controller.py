import random
import subprocess
import sys
import unittest
from pathlib import Path

import combat_controller as controller_module
from abilities import Ability
from ability_effects import HealEffect
from characters import Character
from actions import Action
from combat import Combat
from combat_controller import (
  AbilitySelection,
  CombatController,
  FightOver,
  HeroSelection,
  SelectionState,
  TargetSelection,
)
from enemy_behavior import RandomBehavior
from enemy_data import DEFIAS_MINER, DEVIATE_RAVAGER, RAGEFIRE_TROG
from hero_data import BRAEKS, GENJO, KORYNE
from lib.types import SpellSchool, TargetType

# Koryne's abilities: 0 Arcane Blast (single enemy), 1 Arcane Explosion
# (all enemies), 2 Arcane Barrier (self), 3 basic attack.
BLAST, EXPLOSION, BARRIER, BASIC = 0, 1, 2, 3


def seeded(enemy, seed=0):
  enemy.behavior = RandomBehavior(random.Random(seed))
  return enemy


def make_controller(enemies=None, heroes=None):
  heroes = heroes if heroes is not None else [
    KORYNE.clone(), GENJO.clone(), BRAEKS.clone()
  ]
  enemies = enemies if enemies is not None else [
    seeded(RAGEFIRE_TROG.clone()),
    seeded(DEFIAS_MINER.clone(), 1),
    seeded(RAGEFIRE_TROG.clone(), 2),
  ]
  controller = CombatController(Combat(heroes, enemies))
  return controller, heroes, enemies


def action_of(controller, actor):
  action = controller.combat.action_for(actor)
  assert action is not None
  return action


def choose(controller, hero_index, ability_index):
  """Hero selection -> ability selection, with the cursor on the ability."""
  controller.hero_index = hero_index
  controller.confirm()
  for _ in range(ability_index):
    controller.move(1)


def queue_for_everyone(controller):
  """Give every living hero some action (the first usable one, first target)."""
  for index, hero in enumerate(controller.combat.heroes):
    if not hero.is_alive():
      continue

    choose(controller, index, 0)
    controller.state.confirm()
    if isinstance(controller.state, TargetSelection):
      controller.state.confirm()


class TestStartOfFight(unittest.TestCase):

  def test_starts_in_hero_selection_on_the_first_hero(self):
    controller, heroes, _ = make_controller()

    self.assertIsInstance(controller.state, HeroSelection)
    self.assertIs(controller.selected_hero, heroes[0])

  def test_enemies_have_already_chosen_what_to_do(self):
    controller, _, enemies = make_controller()

    for enemy in enemies:
      self.assertIsNotNone(controller.combat.action_for(enemy))
      self.assertIn("->", controller.intent_text(enemy))

  def test_an_enemy_with_no_abilities_shows_its_basic_attack(self):
    controller, _, _ = make_controller(
      enemies=[seeded(DEVIATE_RAVAGER.clone())]
    )

    self.assertTrue(
      controller.intent_text(controller.combat.enemies[0]).startswith(
        "Basic Attack -> "
      )
    )

  def test_area_intents_report_the_number_of_targets(self):
    sweep = Ability(
      "Sweep", "", 10, 1, TargetType.ALL_ENEMIES, SpellSchool.PHYSICAL
    )
    sweeper = seeded(RAGEFIRE_TROG.clone())
    sweeper.abilities = [sweep]
    controller, _, _ = make_controller(enemies=[sweeper])

    sweep_on_everyone = Action(sweeper, sweep, controller.combat.heroes)
    self.assertEqual(
      controller.describe_action(sweep_on_everyone), "Sweep -> 3 targets"
    )

  def test_first_hero_is_skipped_if_dead(self):
    heroes = [KORYNE.clone(), GENJO.clone(), BRAEKS.clone()]
    heroes[0].take_damage(10_000)

    controller, _, _ = make_controller(heroes=heroes)

    self.assertIs(controller.selected_hero, heroes[1])

  def test_no_hero_has_queued_anything_yet(self):
    controller, heroes, _ = make_controller()

    for hero in heroes:
      self.assertEqual(controller.queued_text(hero), "")
    self.assertFalse(controller.can_resolve)


class TestHeroSelection(unittest.TestCase):

  def test_cursor_moves_and_wraps(self):
    controller, heroes, _ = make_controller()

    controller.move(1)
    self.assertIs(controller.selected_hero, heroes[1])
    controller.move(1)
    controller.move(1)
    self.assertIs(controller.selected_hero, heroes[0])
    controller.move(-1)
    self.assertIs(controller.selected_hero, heroes[2])

  def test_dead_heroes_are_skipped(self):
    controller, heroes, _ = make_controller()
    heroes[1].take_damage(10_000)

    controller.move(1)

    self.assertIs(controller.selected_hero, heroes[2])

  def test_dead_heroes_are_skipped_going_left_too(self):
    controller, heroes, _ = make_controller()
    heroes[2].take_damage(10_000)

    controller.move(-1)

    self.assertIs(controller.selected_hero, heroes[1])

  def test_confirm_opens_ability_selection_from_the_first_ability(self):
    controller, _, _ = make_controller()
    controller.ability_index = 2

    controller.confirm()

    self.assertIsInstance(controller.state, AbilitySelection)
    self.assertEqual(controller.ability_index, 0)

  def test_cancel_does_nothing(self):
    controller, _, _ = make_controller()

    controller.cancel()

    self.assertIsInstance(controller.state, HeroSelection)


class TestAbilitySelection(unittest.TestCase):

  def test_cursor_covers_the_abilities_plus_the_basic_attack_and_wraps(self):
    controller, heroes, _ = make_controller()
    choose(controller, 0, 0)

    self.assertEqual(len(controller.selectable_abilities), 4)
    controller.move(-1)
    self.assertIs(controller.selected_ability, heroes[0].basic_attack)
    controller.move(1)
    self.assertIs(controller.selected_ability, heroes[0].abilities[0])

  def test_cancel_goes_back_to_hero_selection(self):
    controller, _, _ = make_controller()
    choose(controller, 0, 0)

    controller.cancel()

    self.assertIsInstance(controller.state, HeroSelection)

  def test_single_target_ability_opens_target_selection(self):
    controller, _, _ = make_controller()
    choose(controller, 0, BLAST)

    controller.confirm()

    self.assertIsInstance(controller.state, TargetSelection)
    self.assertIsNone(controller.combat.action_for(controller.selected_hero))

  def test_self_ability_queues_immediately(self):
    controller, heroes, _ = make_controller()
    choose(controller, 0, BARRIER)

    controller.confirm()

    self.assertEqual(action_of(controller, heroes[0]).targets, [heroes[0]])
    self.assertIsInstance(controller.state, HeroSelection)

  def test_area_ability_queues_immediately_on_every_living_enemy(self):
    controller, heroes, enemies = make_controller()
    enemies[2].take_damage(10_000)
    choose(controller, 0, EXPLOSION)

    controller.confirm()

    self.assertEqual(action_of(controller, heroes[0]).targets, enemies[:2])
    self.assertIsInstance(controller.state, HeroSelection)

  def test_an_ability_on_cooldown_cannot_be_chosen(self):
    controller, heroes, _ = make_controller()
    heroes[0].abilities[BLAST].use()
    choose(controller, 0, BLAST)

    controller.confirm()

    self.assertIsInstance(controller.state, AbilitySelection)
    self.assertIsNone(controller.combat.action_for(heroes[0]))

  def test_basic_attack_can_be_chosen_while_abilities_are_ready(self):
    controller, heroes, _ = make_controller()
    choose(controller, 0, BASIC)

    self.assertTrue(controller.is_usable(heroes[0].basic_attack))
    controller.confirm()
    self.assertIsInstance(controller.state, TargetSelection)
    controller.confirm()

    self.assertIs(action_of(controller, heroes[0]).ability, heroes[0].basic_attack)

  def test_basic_attack_is_still_usable_when_every_ability_is_on_cooldown(self):
    controller, heroes, _ = make_controller()
    for ability in heroes[0].abilities:
      ability.use()
    choose(controller, 0, BASIC)

    self.assertTrue(controller.is_usable(heroes[0].basic_attack))
    controller.confirm()
    self.assertIsInstance(controller.state, TargetSelection)
    controller.confirm()

    action = action_of(controller, heroes[0])
    self.assertIs(action.ability, heroes[0].basic_attack)


class TestTargetSelection(unittest.TestCase):

  def open_targets(self, controller):
    choose(controller, 0, BLAST)
    controller.confirm()

  def test_confirming_queues_the_action_on_the_highlighted_enemy(self):
    controller, heroes, enemies = make_controller()
    self.open_targets(controller)

    controller.move(1)
    controller.confirm()

    action = action_of(controller, heroes[0])
    self.assertEqual(action.targets, [enemies[1]])
    self.assertEqual(
      controller.queued_text(heroes[0]), "Arcane Blast -> Defias Miner"
    )
    self.assertIsInstance(controller.state, HeroSelection)

  def test_cursor_skips_dead_enemies(self):
    controller, heroes, enemies = make_controller()
    enemies[0].take_damage(10_000)
    self.open_targets(controller)

    controller.confirm()

    self.assertEqual(action_of(controller, heroes[0]).targets, [enemies[1]])

  def test_cursor_wraps_around_living_enemies(self):
    controller, heroes, enemies = make_controller()
    enemies[1].take_damage(10_000)
    self.open_targets(controller)

    controller.move(1)
    controller.move(1)
    controller.confirm()

    self.assertEqual(action_of(controller, heroes[0]).targets, [enemies[0]])

  def test_highlighted_target_follows_the_cursor(self):
    controller, _, enemies = make_controller()
    self.open_targets(controller)

    self.assertIs(controller.highlighted_target(), enemies[0])
    controller.move(1)
    self.assertIs(controller.highlighted_target(), enemies[1])
    controller.move(-1)
    controller.move(-1)
    self.assertIs(controller.highlighted_target(), enemies[2])

  def test_nothing_is_highlighted_outside_target_selection(self):
    controller, _, _ = make_controller()

    self.assertIsNone(controller.highlighted_target())
    choose(controller, 0, BLAST)
    self.assertIsNone(controller.highlighted_target())

  def test_cancel_goes_back_to_ability_selection(self):
    controller, heroes, _ = make_controller()
    self.open_targets(controller)

    controller.cancel()

    self.assertIsInstance(controller.state, AbilitySelection)
    self.assertIsNone(controller.combat.action_for(heroes[0]))

  def test_ally_abilities_target_the_party(self):
    controller, heroes, _ = make_controller()
    heroes[0].abilities.append(Ability(
      "Test Heal", "", 25, 1, TargetType.SINGLE_ALLY, SpellSchool.HOLY,
      effects=[HealEffect()]
    ))
    choose(controller, 0, 3)  # the new ability sits before the basic attack

    controller.confirm()
    self.assertIsInstance(controller.state, TargetSelection)
    self.assertEqual(controller.target_candidates(), heroes)

    heroes[1].take_damage(10_000)
    controller.cancel()
    controller.confirm()
    controller.move(1)
    self.assertIs(controller.highlighted_target(), heroes[2])  # dead skipped
    controller.confirm()

    self.assertEqual(action_of(controller, heroes[0]).targets, [heroes[2]])


class TestRechoosing(unittest.TestCase):

  def test_choosing_again_replaces_the_heros_action(self):
    controller, heroes, _ = make_controller()
    choose(controller, 0, BLAST)
    controller.confirm()
    controller.confirm()
    self.assertEqual(
      controller.queued_text(heroes[0]), "Arcane Blast -> Ragefire Trog"
    )

    choose(controller, 0, EXPLOSION)
    controller.confirm()

    self.assertEqual(
      controller.queued_text(heroes[0]), "Arcane Explosion -> 3 targets"
    )
    queued_for_koryne = [
      a for a in controller.combat.combat_round.action_queue.actions
      if a.actor is heroes[0]
    ]
    self.assertEqual(len(queued_for_koryne), 1)

  def test_backing_out_of_a_rechoice_keeps_the_original_action(self):
    controller, heroes, _ = make_controller()
    choose(controller, 0, BLAST)
    controller.confirm()
    controller.confirm()

    choose(controller, 0, EXPLOSION)
    controller.cancel()

    self.assertEqual(
      controller.queued_text(heroes[0]), "Arcane Blast -> Ragefire Trog"
    )

  def test_an_invalid_rechoice_keeps_the_original_action(self):
    controller, heroes, _ = make_controller()
    choose(controller, 0, BLAST)
    controller.confirm()
    controller.confirm()
    heroes[0].abilities[EXPLOSION].use()

    choose(controller, 0, EXPLOSION)
    controller.confirm()

    self.assertEqual(
      controller.queued_text(heroes[0]), "Arcane Blast -> Ragefire Trog"
    )


class TestResolving(unittest.TestCase):

  def test_cannot_resolve_until_every_living_hero_has_an_action(self):
    controller, _, _ = make_controller()

    self.assertFalse(controller.resolve_round())
    self.assertEqual(controller.combat.round_number, 1)

    for index in (0, 1):
      choose(controller, index, BLAST)
      controller.confirm()
      controller.confirm()
    self.assertFalse(controller.can_resolve)
    self.assertFalse(controller.resolve_round())

  def test_dead_heroes_are_not_waited_for(self):
    controller, heroes, _ = make_controller()
    heroes[2].take_damage(10_000)

    queue_for_everyone(controller)

    self.assertTrue(controller.can_resolve)

  def test_resolving_runs_the_round_and_fills_the_log(self):
    controller, _, _ = make_controller()
    queue_for_everyone(controller)

    ran = controller.resolve_round()

    self.assertTrue(ran)
    self.assertEqual(controller.combat.round_number, 2)
    self.assertGreater(len(controller.log), 0)
    self.assertTrue(all(hasattr(r, "description") for r in controller.log))

  def test_after_a_round_enemies_have_planned_the_next_one(self):
    controller, _, enemies = make_controller()
    queue_for_everyone(controller)

    controller.resolve_round()

    for enemy in enemies:
      if enemy.is_alive():
        self.assertIsNotNone(controller.combat.action_for(enemy))

  def test_after_a_round_heroes_must_choose_again(self):
    controller, heroes, _ = make_controller()
    queue_for_everyone(controller)

    controller.resolve_round()

    for hero in heroes:
      if hero.is_alive():
        self.assertEqual(controller.queued_text(hero), "")
    self.assertFalse(controller.can_resolve)
    self.assertIsInstance(controller.state, HeroSelection)

  def test_resolving_from_the_middle_of_a_selection_resets_to_hero_selection(self):
    controller, _, _ = make_controller()
    queue_for_everyone(controller)
    choose(controller, 0, BLAST)
    self.assertIsInstance(controller.state, AbilitySelection)

    controller.resolve_round()

    self.assertIsInstance(controller.state, HeroSelection)

  def test_cursor_leaves_a_hero_who_died_this_round(self):
    heroes = [Character("Fragile", "Test", 1, 0, 0, 1), BRAEKS.clone()]
    killer = seeded(RAGEFIRE_TROG.clone())
    killer.speed = 99
    controller, _, _ = make_controller(enemies=[killer], heroes=heroes)
    # make sure the Trog goes for the fragile hero
    controller.combat.cancel_action(killer)
    controller.combat.queue_action(killer, killer.abilities[0], [heroes[0]])
    controller.hero_index = 0
    queue_for_everyone(controller)

    controller.resolve_round()

    self.assertFalse(heroes[0].is_alive())
    self.assertIs(controller.selected_hero, heroes[1])

  def test_cooldowns_show_up_after_a_round(self):
    controller, heroes, _ = make_controller()
    queue_for_everyone(controller)   # Koryne used Arcane Blast (cooldown 2)

    controller.resolve_round()

    self.assertFalse(controller.is_usable(heroes[0].abilities[BLAST]))
    self.assertEqual(heroes[0].abilities[BLAST].current_cooldown, 1)

  def test_basic_attack_unlocks_in_the_round_nothing_is_ready(self):
    # Regression: Genjo's three abilities are all on cooldown in round 4.
    genjo = GENJO.clone()
    sturdy_enemy = seeded(RAGEFIRE_TROG.clone())
    sturdy_enemy.health = sturdy_enemy.max_health = 100_000
    controller, _, _ = make_controller(enemies=[sturdy_enemy], heroes=[genjo])

    for ability_index in (1, 2, 0):  # Evasion, Cloak of Shadows, Backstab
      choose(controller, 0, ability_index)
      controller.confirm()
      if isinstance(controller.state, TargetSelection):
        controller.confirm()
      self.assertTrue(controller.resolve_round())

    choose(controller, 0, BASIC)
    self.assertTrue(controller.is_usable(genjo.basic_attack))
    controller.confirm()
    controller.confirm()

    self.assertTrue(controller.can_resolve)
    self.assertTrue(controller.resolve_round())


class TestFightEnd(unittest.TestCase):

  def win(self):
    heroes = [BRAEKS.clone()]
    enemy = seeded(RAGEFIRE_TROG.clone())
    enemy.health = 1
    controller, _, _ = make_controller(enemies=[enemy], heroes=heroes)
    choose(controller, 0, 0)
    controller.confirm()
    controller.confirm()
    controller.resolve_round()
    return controller

  def lose(self):
    hero = Character("Fragile", "Test", 1, 0, 0, 1)
    enemy = seeded(RAGEFIRE_TROG.clone())
    enemy.speed = 99
    controller, _, _ = make_controller(enemies=[enemy], heroes=[hero])
    controller.combat.cancel_action(enemy)
    controller.combat.queue_action(enemy, enemy.abilities[0], [hero])
    choose(controller, 0, BASIC)
    # the lone hero has no abilities, so only the basic attack is usable
    controller.confirm()
    controller.confirm()
    controller.resolve_round()
    return controller

  def test_victory(self):
    controller = self.win()

    self.assertTrue(controller.is_over)
    self.assertTrue(controller.heroes_won)
    self.assertIsInstance(controller.state, FightOver)
    self.assertGreater(len(controller.log), 0)

  def test_defeat(self):
    controller = self.lose()

    self.assertTrue(controller.is_over)
    self.assertFalse(controller.heroes_won)
    self.assertIsInstance(controller.state, FightOver)

  def test_nothing_responds_once_the_fight_is_over(self):
    controller = self.win()
    state = controller.state

    controller.move(1)
    controller.confirm()
    controller.cancel()

    self.assertIs(controller.state, state)
    self.assertFalse(controller.resolve_round())

  def test_round_does_not_advance_after_the_fight_ends(self):
    controller = self.win()

    self.assertEqual(controller.combat.round_number, 1)


class TestFightEndedFromOutside(unittest.TestCase):
  """The controller follows Combat, however the fight happened to end."""

  def test_state_becomes_fight_over_as_soon_as_combat_is_over(self):
    controller, _, enemies = make_controller()
    choose(controller, 0, BLAST)
    self.assertIsInstance(controller.state, AbilitySelection)

    for enemy in enemies:
      enemy.take_damage(10_000)

    self.assertIsInstance(controller.state, FightOver)

  def test_input_is_ignored_once_the_fight_is_over(self):
    controller, _, enemies = make_controller()
    for enemy in enemies:
      enemy.take_damage(10_000)

    controller.confirm()
    controller.move(1)

    self.assertIsInstance(controller.state, FightOver)
    self.assertEqual(controller.hero_index, 0)


class TestStatesAreInterchangeable(unittest.TestCase):

  def test_every_state_implements_the_same_interface(self):
    controller, _, _ = make_controller()

    for state_class in (HeroSelection, AbilitySelection, TargetSelection, FightOver):
      state = state_class(controller)
      self.assertIsInstance(state, SelectionState)
      self.assertTrue(state.hint)

  def test_abstract_state_cannot_be_instantiated(self):
    controller, _, _ = make_controller()

    with self.assertRaises(TypeError):
      SelectionState(controller)  # pyright: ignore[reportAbstractUsage]

  def test_controller_does_not_depend_on_pygame(self):
    src = str(Path(controller_module.__file__).parent)
    code = "import combat_controller, sys; sys.exit('pygame' in sys.modules)"

    result = subprocess.run(
      [sys.executable, "-c", code], cwd=src, capture_output=True
    )

    self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == "__main__":
  unittest.main()
