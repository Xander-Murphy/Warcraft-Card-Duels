import unittest

import pygame

from game import Game
from hero_data import BRAEKS, GENJO, KORYNE
from screens.end_screens import GameOverScreen, GameWonScreen
from states import GameState


def press_enter(screen, game):
  screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN), game)


class TestFinishCombat(unittest.TestCase):

  def setUp(self):
    self.game = Game(None)
    self.game.selected_heroes = [KORYNE, GENJO, BRAEKS]
    self.game.selected_dungeon = "Wailing Caverns"
    self.game.start_run()
    self.game.state = GameState.COMBAT

  def test_winning_an_encounter_counts_it_and_returns_to_the_dungeon(self):
    self.game.finish_combat(True)

    self.assertEqual(self.game.current_encounter, 1)
    self.assertEqual(self.game.state, GameState.DUNGEON)

  def test_winning_the_last_encounter_wins_the_dungeon(self):
    self.game.current_encounter = self.game.total_encounters - 1

    self.game.finish_combat(True)

    self.assertEqual(self.game.state, GameState.GAME_WON)

  def test_losing_ends_the_run_without_counting_the_encounter(self):
    self.game.finish_combat(False)

    self.assertEqual(self.game.current_encounter, 0)
    self.assertEqual(self.game.state, GameState.GAME_OVER)

  def test_the_fight_is_cleared_either_way(self):
    self.game.start_combat()

    self.game.finish_combat(True)

    self.assertIsNone(self.game.combat)

  def test_the_party_carries_damage_cooldowns_and_deaths_into_the_next_fight(self):
    koryne, genjo, braeks = self.game.party
    koryne.take_damage(30)
    genjo.abilities[0].use()
    braeks.take_damage(10_000)
    health_before = koryne.health

    self.game.finish_combat(True)

    self.assertEqual(self.game.party[0].health, health_before)
    self.assertGreater(self.game.party[1].abilities[0].current_cooldown, 0)
    self.assertFalse(self.game.party[2].is_alive())

  def test_starting_a_new_run_resets_progress_and_heals_the_party(self):
    self.game.finish_combat(True)
    self.game.party[0].take_damage(30)

    self.game.start_run()

    self.assertEqual(self.game.current_encounter, 0)
    self.assertEqual(self.game.party[0].health, self.game.party[0].max_health)


class TestEndScreens(unittest.TestCase):

  def setUp(self):
    self.game = Game(None)
    self.game.selected_heroes = [KORYNE]
    self.game.selected_dungeon = "The Deadmines"
    self.game.start_run()

  def test_game_over_enter_returns_to_the_main_menu(self):
    self.game.state = GameState.GAME_OVER

    press_enter(GameOverScreen(), self.game)

    self.assertEqual(self.game.state, GameState.MAIN_MENU)

  def test_dungeon_cleared_enter_returns_to_dungeon_selection(self):
    self.game.state = GameState.GAME_WON

    press_enter(GameWonScreen(), self.game)

    self.assertEqual(self.game.state, GameState.DUNGEON_SELECTION)

  def test_other_keys_do_not_leave_the_screen(self):
    self.game.state = GameState.GAME_OVER

    GameOverScreen().handle_input(
      pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE), self.game
    )

    self.assertEqual(self.game.state, GameState.GAME_OVER)

  def test_both_screens_are_registered_with_the_game(self):
    self.assertIsInstance(self.game.screens[GameState.GAME_OVER], GameOverScreen)
    self.assertIsInstance(self.game.screens[GameState.GAME_WON], GameWonScreen)

  def test_both_screens_draw_the_party_without_error(self):
    surface = pygame.Surface((1000, 700))
    pygame.font.init()
    self.game.party[0].take_damage(10_000)

    for screen in (GameOverScreen(), GameWonScreen()):
      screen.draw(surface, self.game)
