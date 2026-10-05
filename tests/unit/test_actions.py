import unittest

from actions import Action
from hero_data import KORYNE, GENJO
from enemy_data import RAGEFIRE_TROG
from ability_data.hero_abilities import ARCANE_BLAST, CLOAK_OF_SHADOWS


class TestActions(unittest.TestCase):

  def test_action_priority(self):
    normal_action = Action(
      KORYNE,
      ARCANE_BLAST,
      [RAGEFIRE_TROG]
    )

    priority_action = Action(
      GENJO,
      CLOAK_OF_SHADOWS,
      [GENJO]
    )

    self.assertEqual(normal_action.priority, 7)
    self.assertEqual(priority_action.priority, 19)


if __name__ == "__main__":
  unittest.main()