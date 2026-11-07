import os
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game import Game
from screens.hero_details import HeroDetails
from screens.team_selection import TeamSelectionScreen
from states import GameState


class TestTeamSelectionDetails(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    pygame.init()
    cls.surface = pygame.display.set_mode((1000, 700))

  @classmethod
  def tearDownClass(cls):
    pygame.quit()

  def setUp(self):
    self.game = Game(None)
    self.game.state = GameState.TEAM_SELECTION
    self.screen = TeamSelectionScreen()

  def shown_hero(self):
    with mock.patch.object(HeroDetails, "draw") as draw:
      self.screen.draw(self.surface, self.game)
    return draw.call_args.args[1]

  def test_details_follow_the_cursor(self):
    self.assertIs(self.shown_hero(), self.game.available_heroes[0])

    self.screen.handle_input(
      pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN), self.game
    )

    self.assertIs(self.shown_hero(), self.game.available_heroes[1])

  def test_all_eight_heroes_can_be_picked(self):
    from hero_data import (
      BRAEKS, GENJO, KORYNE, LIORA, SCATTER, TAMARU, TORVALD, VESK
    )

    self.assertEqual(
      self.game.available_heroes,
      [KORYNE, GENJO, SCATTER, BRAEKS, LIORA, TORVALD, VESK, TAMARU],
    )

    for _ in range(4):  # down to Liora, the first new hero
      self.screen.handle_input(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN), self.game
      )
    self.screen.handle_input(
      pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE), self.game
    )

    self.assertEqual(self.game.selected_heroes, [LIORA])

  def test_every_hero_draws_without_error(self):
    for hero in self.game.available_heroes:
      HeroDetails().draw(self.surface, hero, (420, 150))
