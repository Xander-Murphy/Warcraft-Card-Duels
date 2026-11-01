import unittest

from hero_data import KORYNE
from screens.widgets import status_line


class TestStatusLine(unittest.TestCase):

  def test_a_living_character_shows_current_and_max_health(self):
    koryne = KORYNE.clone()
    koryne.take_damage(30)

    self.assertEqual(status_line(koryne), f"Koryne - HP {koryne.health}/75")

  def test_a_defeated_character_says_so_instead_of_zero_health(self):
    koryne = KORYNE.clone()
    koryne.take_damage(10_000)

    self.assertEqual(status_line(koryne), "Koryne - Defeated")
