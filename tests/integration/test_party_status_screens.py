import os
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from enemy_data import DEFIAS_MINER
from game import Game
from hero_data import BRAEKS, KORYNE, SCATTER
from screens import widgets
from screens.dungeon import DungeonScreen
from screens.encounter import EncounterScreen


class PartyStatusTestCase(unittest.TestCase):
  """A run part-way through: one hero hurt, one defeated."""

  @classmethod
  def setUpClass(cls):
    pygame.init()
    cls.surface = pygame.display.set_mode((1000, 700))

  @classmethod
  def tearDownClass(cls):
    pygame.quit()

  def setUp(self):
    self.game = Game(None)
    self.game.selected_heroes = [KORYNE, SCATTER, BRAEKS]
    self.game.selected_dungeon = "The Deadmines"
    self.game.start_run()
    self.game.current_encounter = 1
    self.game.party[0].take_damage(30)
    self.game.party[2].take_damage(10_000)
    self.game.current_enemies = [DEFIAS_MINER.clone()]

  def drawn_text(self, screen):
    drawn = []
    original = widgets.draw_text

    def record(surface, font, text, color, center):
      drawn.append(text)
      original(surface, font, text, color, center)

    # Each screen imported draw_text by name, so patch it where it is used
    module = type(screen).__module__
    with mock.patch(f"{module}.draw_text", record), \
         mock.patch.object(widgets, "draw_text", record):
      screen.draw(self.surface, self.game)

    return drawn


class TestDungeonScreen(PartyStatusTestCase):

  def test_shows_progress_and_every_heros_status(self):
    shown = self.drawn_text(DungeonScreen())
    koryne = self.game.party[0]

    self.assertIn("Encounter 2 / 3", shown)
    self.assertIn(f"Koryne - HP {koryne.health}/75", shown)
    self.assertIn("Scatter - HP 95/95", shown)
    self.assertIn("Braeks - Defeated", shown)

  def test_no_longer_promises_a_boss(self):
    shown = self.drawn_text(DungeonScreen())

    self.assertFalse(any("Boss" in text for text in shown))


class TestEncounterScreen(PartyStatusTestCase):

  def test_shows_the_enemies_health_and_the_party(self):
    shown = self.drawn_text(EncounterScreen())

    self.assertIn("Defias Miner - HP 47/47", shown)
    self.assertIn("Braeks - Defeated", shown)

  def test_the_instructions_are_drawn_once(self):
    self.game.current_enemies = [DEFIAS_MINER.clone() for _ in range(3)]

    shown = self.drawn_text(EncounterScreen())

    self.assertEqual(shown.count("Enter: Begin Combat | Escape: Back"), 1)
