import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from abilities import Ability
from ability_effects import HealEffect
from enemy_data import DEFIAS_MINER, RAGEFIRE_TROG
from game import Game
from hero_data import BRAEKS, GENJO, KORYNE
from lib.types import SpellSchool, TargetType
from screens.combat import CombatScreen


def press(screen, game, key):
  screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=key), game)


class CombatScreenTestCase(unittest.TestCase):

  def setUp(self):
    self.game = Game(None)
    self.game.selected_heroes = [KORYNE, GENJO, BRAEKS]
    self.game.start_run()
    self.game.selected_dungeon = "Wailing Caverns"
    self.game.current_enemies = [
      RAGEFIRE_TROG.clone(), DEFIAS_MINER.clone(), RAGEFIRE_TROG.clone()
    ]
    self.screen = CombatScreen()

  def press(self, *keys):
    for key in keys:
      press(self.screen, self.game, key)

  def choose_ability(self, hero_index, ability_index):
    """Hero select -> ability select, leaving the cursor on the ability."""
    self.screen.hero_selection = hero_index
    self.press(pygame.K_SPACE)
    for _ in range(ability_index):
      self.press(pygame.K_RIGHT)

  @property
  def queued(self):
    return self.screen.combat_round.action_queue.actions


class TestSingleTargetAbilities(CombatScreenTestCase):

  def test_single_enemy_ability_opens_target_mode(self):
    self.choose_ability(0, 0)  # Koryne: Arcane Blast

    self.press(pygame.K_SPACE)

    self.assertEqual(self.screen.selection_mode, "target")
    self.assertEqual(self.queued, [])

  def test_confirming_a_target_queues_an_action_on_that_enemy(self):
    self.choose_ability(0, 0)

    self.press(pygame.K_SPACE, pygame.K_RIGHT, pygame.K_SPACE)

    self.assertEqual(len(self.queued), 1)
    self.assertIs(self.queued[0].actor, self.game.party[0])
    self.assertEqual(self.queued[0].targets, [self.game.current_enemies[1]])
    self.assertEqual(self.screen.selection_mode, "hero")

  def test_target_cursor_skips_dead_enemies(self):
    self.game.current_enemies[0].take_damage(10_000)
    self.choose_ability(0, 0)

    self.press(pygame.K_SPACE, pygame.K_SPACE)  # first living target

    self.assertEqual(self.queued[0].targets, [self.game.current_enemies[1]])

  def test_target_cursor_wraps_around_living_enemies(self):
    self.game.current_enemies[1].take_damage(10_000)
    self.choose_ability(0, 0)

    # two living enemies: right twice wraps back to the first
    self.press(pygame.K_SPACE, pygame.K_RIGHT, pygame.K_RIGHT, pygame.K_SPACE)

    self.assertEqual(self.queued[0].targets, [self.game.current_enemies[0]])

  def test_escape_in_target_mode_returns_to_ability_mode(self):
    self.choose_ability(0, 0)

    self.press(pygame.K_SPACE, pygame.K_ESCAPE)

    self.assertEqual(self.screen.selection_mode, "ability")
    self.assertEqual(self.queued, [])

  def test_no_living_enemies_means_no_target_mode(self):
    for enemy in self.game.current_enemies:
      enemy.take_damage(10_000)
    self.choose_ability(0, 0)

    self.press(pygame.K_SPACE)

    self.assertEqual(self.screen.selection_mode, "ability")
    self.assertEqual(self.queued, [])


class TestAutomaticTargeting(CombatScreenTestCase):

  def test_self_ability_queues_immediately_on_the_caster(self):
    self.choose_ability(0, 2)  # Koryne: Arcane Barrier (SELF)

    self.press(pygame.K_SPACE)

    self.assertEqual(len(self.queued), 1)
    self.assertEqual(self.queued[0].targets, [self.game.party[0]])
    self.assertEqual(self.screen.selection_mode, "hero")

  def test_all_enemies_ability_queues_immediately_on_every_living_enemy(self):
    self.game.current_enemies[2].take_damage(10_000)
    self.choose_ability(2, 2)  # Braeks: Whirlwind (ALL_ENEMIES)

    self.press(pygame.K_SPACE)

    self.assertEqual(len(self.queued), 1)
    self.assertEqual(
      self.queued[0].targets,
      [self.game.current_enemies[0], self.game.current_enemies[1]]
    )
    self.assertEqual(self.screen.selection_mode, "hero")

  def test_queued_area_action_actually_resolves(self):
    self.choose_ability(2, 2)
    self.press(pygame.K_SPACE)

    results = self.queued[0].execute()

    self.assertEqual(len(results), 3)
    self.assertTrue(
      all(e.health < e.max_health for e in self.game.current_enemies)
    )


class TestAllyTargeting(CombatScreenTestCase):
  """No ability in the data targets a single ally yet, so give one a heal."""

  def setUp(self):
    super().setUp()
    self.game.party[0].abilities.append(Ability(
      "Test Heal", "", 25, 1, TargetType.SINGLE_ALLY, SpellSchool.HOLY,
      effects=[HealEffect()]
    ))
    self.heal_index = len(self.game.party[0].abilities) - 1

  def test_ally_ability_targets_the_party_not_the_enemies(self):
    self.choose_ability(0, self.heal_index)

    self.press(pygame.K_SPACE)

    self.assertEqual(self.screen.selection_mode, "target")
    self.assertEqual(
      self.screen._target_candidates(self.game), self.game.party
    )

  def test_confirming_queues_the_chosen_ally(self):
    self.choose_ability(0, self.heal_index)

    self.press(pygame.K_SPACE, pygame.K_RIGHT, pygame.K_SPACE)

    self.assertEqual(self.queued[0].targets, [self.game.party[1]])

  def test_highlight_lands_on_the_ally_and_draws(self):
    pygame.init()
    surface = pygame.display.set_mode((1000, 700))
    self.choose_ability(0, self.heal_index)
    self.press(pygame.K_SPACE, pygame.K_RIGHT)

    self.assertIs(
      self.screen._highlighted_target(self.game), self.game.party[1]
    )
    self.screen.draw(surface, self.game)

  def test_dead_allies_are_skipped(self):
    self.game.party[1].take_damage(10_000)
    self.choose_ability(0, self.heal_index)

    self.press(pygame.K_SPACE, pygame.K_RIGHT, pygame.K_SPACE)

    self.assertEqual(self.queued[0].targets, [self.game.party[2]])


class TestDrawing(CombatScreenTestCase):

  @classmethod
  def setUpClass(cls):
    pygame.init()
    cls.surface = pygame.display.set_mode((1000, 700))

  @classmethod
  def tearDownClass(cls):
    pygame.quit()

  def test_draw_works_in_every_selection_mode(self):
    self.screen.draw(self.surface, self.game)           # hero
    self.choose_ability(0, 0)
    self.screen.draw(self.surface, self.game)           # ability
    self.press(pygame.K_SPACE)
    self.screen.draw(self.surface, self.game)           # target

  def test_highlighted_target_follows_the_cursor(self):
    self.choose_ability(0, 0)
    self.press(pygame.K_SPACE, pygame.K_RIGHT)

    self.assertIs(
      self.screen._highlighted_target(self.game),
      self.game.current_enemies[1]
    )

  def test_no_highlighted_target_outside_target_mode(self):
    self.assertIsNone(self.screen._highlighted_target(self.game))


if __name__ == "__main__":
  unittest.main()
