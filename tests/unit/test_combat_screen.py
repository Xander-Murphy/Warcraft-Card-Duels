import os
import random
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from combat import Combat
from combat_controller import (
  AbilitySelection, FightOver, HeroSelection, TargetSelection
)
from enemy_behavior import RandomBehavior
from enemy_data import DEFIAS_MINER, RAGEFIRE_TROG
from game import Game
from hero_data import BRAEKS, GENJO, KORYNE
from screens.combat import CombatScreen
from screens.encounter import EncounterScreen
from states import GameState


def key(screen, game, pygame_key):
  screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame_key), game)


def seeded(enemy, seed=0):
  enemy.behavior = RandomBehavior(random.Random(seed))
  return enemy


class ScreenTestCase(unittest.TestCase):

  def setUp(self):
    self.game = Game(None)
    self.game.selected_heroes = [KORYNE, GENJO, BRAEKS]
    self.game.start_run()
    self.game.selected_dungeon = "Wailing Caverns"
    self.game.current_enemies = [
      seeded(RAGEFIRE_TROG.clone()),
      seeded(DEFIAS_MINER.clone(), 1),
      seeded(RAGEFIRE_TROG.clone(), 2),
    ]
    self.game.start_combat()
    self.screen = CombatScreen()

  def press(self, *keys):
    for pygame_key in keys:
      key(self.screen, self.game, pygame_key)

  @property
  def combat(self):
    assert self.game.combat is not None
    return self.game.combat

  @property
  def controller(self):
    # The screen builds its controller on first use
    controller = self.screen._controller_for(self.game)
    assert controller is not None
    return controller

  def queue_everyone(self):
    # Every hero picks their first ability (and first target if needed)
    for hero_index in range(len(self.combat.heroes)):
      self.controller.hero_index = hero_index
      self.press(pygame.K_SPACE, pygame.K_SPACE)
      if isinstance(self.controller.state, TargetSelection):
        self.press(pygame.K_SPACE)


class TestKeyMapping(ScreenTestCase):

  def test_arrow_keys_and_wasd_both_move_the_cursor(self):
    self.press(pygame.K_RIGHT)
    self.assertEqual(self.controller.hero_index, 1)
    self.press(pygame.K_d)
    self.assertEqual(self.controller.hero_index, 2)
    self.press(pygame.K_LEFT)
    self.assertEqual(self.controller.hero_index, 1)
    self.press(pygame.K_a)
    self.assertEqual(self.controller.hero_index, 0)

  def test_space_confirms_and_escape_cancels(self):
    self.press(pygame.K_SPACE)
    self.assertIsInstance(self.controller.state, AbilitySelection)

    self.press(pygame.K_SPACE)
    self.assertIsInstance(self.controller.state, TargetSelection)

    self.press(pygame.K_ESCAPE)
    self.assertIsInstance(self.controller.state, AbilitySelection)

    self.press(pygame.K_ESCAPE)
    self.assertIsInstance(self.controller.state, HeroSelection)

  def test_choosing_an_action_through_the_keys_queues_it(self):
    self.press(pygame.K_SPACE, pygame.K_SPACE, pygame.K_RIGHT, pygame.K_SPACE)

    action = self.combat.action_for(self.game.party[0])
    assert action is not None
    self.assertEqual(action.targets, [self.game.current_enemies[1]])

  def test_enter_does_nothing_until_everyone_has_an_action(self):
    self.game.state = GameState.COMBAT

    self.press(pygame.K_RETURN)

    self.assertEqual(self.combat.round_number, 1)
    self.assertEqual(self.game.state, GameState.COMBAT)

  def test_enter_resolves_the_round_once_everyone_is_ready(self):
    self.queue_everyone()

    self.press(pygame.K_RETURN)

    self.assertEqual(self.combat.round_number, 2)
    self.assertGreater(len(self.controller.log), 0)

  def test_other_keys_are_ignored(self):
    self.press(pygame.K_x, pygame.K_UP, pygame.K_TAB)

    self.assertIsInstance(self.controller.state, HeroSelection)
    self.assertEqual(self.controller.hero_index, 0)


class TestControllerLifecycle(ScreenTestCase):

  def test_input_is_safe_without_a_fight(self):
    self.game.end_combat()
    self.press(pygame.K_SPACE, pygame.K_RETURN)

    self.assertIsNone(self.screen.controller)

  def test_the_same_fight_keeps_the_same_controller(self):
    self.press(pygame.K_RIGHT)
    first = self.controller

    self.press(pygame.K_RIGHT)

    self.assertIs(self.controller, first)
    self.assertEqual(first.hero_index, 2)

  def test_a_new_fight_gets_a_fresh_controller(self):
    self.press(pygame.K_RIGHT, pygame.K_SPACE)
    old = self.controller

    self.game.start_combat()
    self.press(pygame.K_RIGHT)

    self.assertIsNot(self.controller, old)
    self.assertIsInstance(self.controller.state, HeroSelection)
    self.assertEqual(self.controller.hero_index, 1)  # started again from hero 0

  def test_leaving_a_fight_forgets_the_controller(self):
    self.press(pygame.K_RIGHT)
    self.game.end_combat()
    self.press(pygame.K_RIGHT)

    self.assertIsNone(self.screen.controller)


class TestEndOfFight(ScreenTestCase):

  def finish_fight(self, hero_wins):
    if hero_wins:
      for enemy in self.game.current_enemies:
        enemy.take_damage(10_000)
    else:
      for hero in self.game.party:
        hero.take_damage(10_000)

  def test_enter_after_a_win_returns_to_the_dungeon(self):
    self.game.state = GameState.COMBAT
    self.press(pygame.K_RIGHT)       # make the controller
    self.finish_fight(hero_wins=True)

    self.press(pygame.K_RETURN)

    self.assertEqual(self.game.state, GameState.DUNGEON)
    self.assertIsNone(self.game.combat)

  def test_enter_after_a_loss_returns_to_the_main_menu(self):
    self.game.state = GameState.COMBAT
    self.press(pygame.K_RIGHT)
    self.finish_fight(hero_wins=False)

    self.press(pygame.K_RETURN)

    self.assertEqual(self.game.state, GameState.MAIN_MENU)
    self.assertIsNone(self.game.combat)

  def test_a_fight_won_by_playing_it_out_ends_in_the_dungeon(self):
    self.game.state = GameState.COMBAT
    lone_enemy = seeded(RAGEFIRE_TROG.clone())
    lone_enemy.health = 1
    self.game.current_enemies = [lone_enemy]
    self.game.start_combat()
    self.queue_everyone()

    self.press(pygame.K_RETURN)
    self.assertIsInstance(self.controller.state, FightOver)
    self.assertEqual(self.game.state, GameState.COMBAT)  # banner first

    self.press(pygame.K_RETURN)
    self.assertEqual(self.game.state, GameState.DUNGEON)

  def test_other_keys_do_nothing_on_the_banner(self):
    self.press(pygame.K_RIGHT)
    self.finish_fight(hero_wins=True)

    self.assertTrue(self.controller.is_over)
    self.press(pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_RIGHT)

    self.assertIsNotNone(self.game.combat)


class TestGameAndEncounterWiring(unittest.TestCase):

  def make_game(self):
    game = Game(None)
    game.selected_heroes = [KORYNE, GENJO]
    game.start_run()
    game.selected_dungeon = "Wailing Caverns"
    game.current_enemies = [RAGEFIRE_TROG.clone()]
    return game

  def test_start_combat_builds_a_fight_from_the_party_and_enemies(self):
    game = self.make_game()

    game.start_combat()

    assert game.combat is not None
    self.assertIsInstance(game.combat, Combat)
    self.assertEqual(game.combat.heroes, game.party)
    self.assertEqual(game.combat.enemies, game.current_enemies)
    self.assertEqual(game.combat.round_number, 1)

  def test_each_start_gives_a_brand_new_fight(self):
    game = self.make_game()

    game.start_combat()
    first = game.combat
    game.start_combat()

    self.assertIsNot(game.combat, first)

  def test_end_combat_clears_the_fight(self):
    game = self.make_game()
    game.start_combat()

    game.end_combat()

    self.assertIsNone(game.combat)

  def test_enter_on_the_encounter_screen_starts_the_fight(self):
    game = self.make_game()
    game.state = GameState.ENCOUNTER

    EncounterScreen().handle_input(
      pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN), game
    )

    self.assertEqual(game.state, GameState.COMBAT)
    self.assertIsNotNone(game.combat)

  def test_escape_on_the_encounter_screen_does_not_start_a_fight(self):
    game = self.make_game()
    game.state = GameState.ENCOUNTER

    EncounterScreen().handle_input(
      pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE), game
    )

    self.assertEqual(game.state, GameState.DUNGEON)
    self.assertIsNone(game.combat)

  def test_a_second_fight_in_the_same_run_starts_clean(self):
    game = self.make_game()
    screen = CombatScreen()

    game.start_combat()
    key(screen, game, pygame.K_RIGHT)
    game.party[0].take_damage(30)          # damage carries over between fights
    game.end_combat()
    game.current_enemies = [RAGEFIRE_TROG.clone()]
    game.start_combat()
    key(screen, game, pygame.K_RIGHT)

    assert screen.controller is not None
    self.assertEqual(screen.controller.hero_index, 1)  # fresh cursor
    self.assertLess(game.party[0].health, game.party[0].max_health)


class TestDrawing(ScreenTestCase):

  @classmethod
  def setUpClass(cls):
    pygame.init()
    cls.surface = pygame.display.set_mode((1000, 700))

  @classmethod
  def tearDownClass(cls):
    pygame.quit()

  def setUp(self):
    super().setUp()
    self.drawn = []
    original = CombatScreen._text

    def record(screen_self, surface, font, text, color, center):
      self.drawn.append(text)
      return original(screen_self, surface, font, text, color, center)

    patcher = mock.patch.object(CombatScreen, "_text", record)
    patcher.start()
    self.addCleanup(patcher.stop)

  def draw(self):
    self.drawn.clear()
    self.screen.draw(self.surface, self.game)
    return list(self.drawn)

  def test_draw_without_a_fight_draws_nothing(self):
    self.game.end_combat()

    self.assertEqual(self.draw(), [])

  def test_shows_title_round_names_and_health(self):
    shown = self.draw()

    self.assertIn("Wailing Caverns - Combat", shown)
    self.assertIn("Round 1", shown)
    for name in ("Koryne", "Genjo", "Braeks", "Ragefire Trog", "Defias Miner"):
      self.assertIn(name, shown)
    self.assertIn(f"HP {KORYNE.max_health}/{KORYNE.max_health}", shown)

  def test_shows_what_each_enemy_plans_to_do(self):
    shown = self.draw()

    intents = [text for text in shown if " -> " in text]
    self.assertEqual(len(intents), 3)

  def test_dead_characters_are_marked_defeated_and_have_no_intent(self):
    self.press(pygame.K_RIGHT)  # make the controller
    self.game.current_enemies[0].take_damage(10_000)
    self.game.party[1].take_damage(10_000)

    shown = self.draw()

    self.assertEqual(shown.count("Defeated"), 2)
    self.assertEqual(len([t for t in shown if " -> " in t]), 2)

  def test_prompts_follow_the_selection_state(self):
    self.assertIn("Choose an action for every hero", self.draw())

    self.queue_everyone()
    self.assertIn("Everyone is ready: press Enter", self.draw())

    self.press(pygame.K_SPACE)
    self.assertIn(self.controller.state.hint, self.draw())

  def test_shows_the_queued_action_under_the_hero(self):
    self.press(pygame.K_SPACE, pygame.K_SPACE, pygame.K_SPACE)

    self.assertIn("Arcane Blast -> Ragefire Trog", self.draw())

  def test_target_prompt_shows_while_choosing_a_target(self):
    self.press(pygame.K_SPACE, pygame.K_SPACE)

    self.assertIn("Select a target", self.draw())

  def test_abilities_show_cooldowns_and_the_locked_basic_attack(self):
    self.game.party[0].abilities[0].use()
    self.press(pygame.K_SPACE)

    shown = self.draw()

    self.assertIn("Arcane Blast (CD 2)", shown)
    self.assertIn("Arcane Explosion", shown)
    self.assertIn("Basic Attack (locked)", shown)

  def test_ability_description_explains_why_something_is_unavailable(self):
    self.game.party[0].abilities[0].use()
    self.press(pygame.K_SPACE)
    self.assertIn("On cooldown: 2 more round(s)", self.draw())

    self.press(pygame.K_LEFT)  # wraps to the basic attack
    self.assertIn(
      "Only usable when none of this hero's abilities are ready", self.draw()
    )

  def test_basic_attack_is_unlocked_when_nothing_else_is_ready(self):
    for ability in self.game.party[0].abilities:
      ability.use()
    self.press(pygame.K_SPACE)

    self.assertIn("Basic Attack", self.draw())
    self.assertNotIn("Basic Attack (locked)", self.draw())

  def test_the_last_rounds_results_are_shown(self):
    self.queue_everyone()
    self.press(pygame.K_RETURN)

    shown = self.draw()

    for result in self.controller.log[-6:]:
      self.assertIn(result.description, shown)
    self.assertIn("Round 2", shown)

  def test_victory_banner(self):
    self.press(pygame.K_RIGHT)
    for enemy in self.game.current_enemies:
      enemy.take_damage(10_000)

    shown = self.draw()

    self.assertIn("VICTORY", shown)
    self.assertNotIn("DEFEAT", shown)
    self.assertIn("Enter: Continue", shown)

  def test_defeat_banner(self):
    self.press(pygame.K_RIGHT)
    for hero in self.game.party:
      hero.take_damage(10_000)

    shown = self.draw()

    self.assertIn("DEFEAT", shown)
    self.assertNotIn("VICTORY", shown)

  def test_banner_hides_the_ability_row(self):
    self.press(pygame.K_RIGHT)
    for enemy in self.game.current_enemies:
      enemy.take_damage(10_000)

    shown = self.draw()

    self.assertNotIn("Arcane Blast", shown)

  def test_every_state_draws_without_error(self):
    self.draw()
    self.press(pygame.K_SPACE)
    self.draw()
    self.press(pygame.K_SPACE)
    self.draw()
    self.press(pygame.K_ESCAPE, pygame.K_ESCAPE)
    self.queue_everyone()
    self.draw()
    self.press(pygame.K_RETURN)
    self.draw()


if __name__ == "__main__":
  unittest.main()
