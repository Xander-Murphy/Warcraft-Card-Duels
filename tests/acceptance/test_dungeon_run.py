"""A player's view of a dungeon run: only key presses go in, only the game's
state comes out. The one shortcut is how a fight is decided, because playing
a whole fight by key presses would depend on chance."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game import Game
from hero_data import BRAEKS, GENJO, KORYNE
from states import GameState


class DungeonRunTestCase(unittest.TestCase):

  def setUp(self):
    pygame.init()
    self.addCleanup(pygame.quit)
    self.game = Game(None)
    self.game.selected_heroes = [KORYNE, GENJO, BRAEKS]
    self.game.selected_dungeon = "Wailing Caverns"
    self.game.state = GameState.DUNGEON_SELECTION

  def press(self, key):
    self.game.screens[self.game.state].handle_input(
      pygame.event.Event(pygame.KEYDOWN, key=key), self.game
    )

  def start_fight(self):
    """From the dungeon screen to the first round of the fight."""
    self.press(pygame.K_RETURN)  # begin the encounter
    self.assertEqual(self.game.state, GameState.ENCOUNTER)
    self.press(pygame.K_RETURN)  # begin combat
    self.assertEqual(self.game.state, GameState.COMBAT)

  def finish_fight(self, heroes_win):
    for side in (self.game.current_enemies if heroes_win else self.game.party):
      side.take_damage(10_000)
    self.press(pygame.K_SPACE)   # lets the screen notice the fight is over
    self.press(pygame.K_RETURN)  # dismiss the VICTORY / DEFEAT banner


class TestClearingADungeon(DungeonRunTestCase):

  def test_winning_every_encounter_clears_the_dungeon(self):
    self.press(pygame.K_RETURN)  # choose the dungeon
    self.assertEqual(self.game.state, GameState.DUNGEON)

    for expected_progress in (1, 2):
      self.start_fight()
      self.finish_fight(heroes_win=True)
      self.assertEqual(self.game.state, GameState.DUNGEON)
      self.assertEqual(self.game.current_encounter, expected_progress)

    self.start_fight()
    self.finish_fight(heroes_win=True)
    self.assertEqual(self.game.state, GameState.GAME_WON)

    self.press(pygame.K_RETURN)
    self.assertEqual(self.game.state, GameState.DUNGEON_SELECTION)

  def test_a_second_run_starts_from_the_first_encounter_with_a_healthy_party(self):
    self.press(pygame.K_RETURN)
    for _ in range(3):
      self.start_fight()
      self.finish_fight(heroes_win=True)
    self.press(pygame.K_RETURN)  # back to dungeon selection

    self.press(pygame.K_RETURN)  # run the same dungeon again

    self.assertEqual(self.game.state, GameState.DUNGEON)
    self.assertEqual(self.game.current_encounter, 0)
    self.assertTrue(all(hero.health == hero.max_health for hero in self.game.party))


class TestLosingADungeon(DungeonRunTestCase):

  def test_a_wiped_party_sees_game_over_and_returns_to_the_main_menu(self):
    self.press(pygame.K_RETURN)
    self.start_fight()
    self.finish_fight(heroes_win=False)
    self.assertEqual(self.game.state, GameState.GAME_OVER)

    self.press(pygame.K_RETURN)
    self.assertEqual(self.game.state, GameState.MAIN_MENU)

  def test_a_party_that_loses_late_has_still_cleared_earlier_encounters(self):
    self.press(pygame.K_RETURN)
    self.start_fight()
    self.finish_fight(heroes_win=True)
    self.start_fight()
    self.finish_fight(heroes_win=False)

    self.assertEqual(self.game.state, GameState.GAME_OVER)
    self.assertEqual(self.game.current_encounter, 1)


class TestInjuriesCarryOver(DungeonRunTestCase):

  def test_a_hero_killed_in_one_fight_is_still_dead_in_the_next(self):
    self.press(pygame.K_RETURN)
    self.start_fight()
    self.game.party[2].take_damage(10_000)
    self.finish_fight(heroes_win=True)

    self.start_fight()

    assert self.game.combat is not None
    self.assertFalse(self.game.party[2].is_alive())
    self.assertEqual(len(self.game.combat.living_heroes()), 2)
