import unittest

from actions import Action
from action_queue import ActionQueue
from hero_data import KORYNE, GENJO, BRAEKS
from enemy_data import RAGEFIRE_TROG
from ability_data.hero_abilities import (
  ARCANE_BLAST,
  CLOAK_OF_SHADOWS,
  HEROIC_STRIKE
)


class TestActionQueue(unittest.TestCase):

  def test_actions_are_sorted_by_priority(self):
    queue = ActionQueue()

    koryne_action = Action(
      KORYNE,
      ARCANE_BLAST,
      [RAGEFIRE_TROG]
    )

    genjo_action = Action(
      GENJO,
      CLOAK_OF_SHADOWS,
      [GENJO]
    )

    braeks_action = Action(
      BRAEKS,
      HEROIC_STRIKE,
      [RAGEFIRE_TROG]
    )

    queue.add_action(koryne_action)
    queue.add_action(genjo_action)
    queue.add_action(braeks_action)

    queue.sort_actions()

    self.assertEqual(queue.actions[0], genjo_action)
    self.assertEqual(queue.actions[1], koryne_action)
    self.assertEqual(queue.actions[2], braeks_action)


  def test_get_next_action_removes_action(self):
    queue = ActionQueue()

    action = Action(
      KORYNE,
      ARCANE_BLAST,
      [RAGEFIRE_TROG]
    )

    queue.add_action(action)

    next_action = queue.get_next_action()

    self.assertEqual(next_action, action)
    self.assertEqual(len(queue.actions), 0)


  def test_empty_queue_returns_none(self):
    queue = ActionQueue()

    self.assertIsNone(queue.get_next_action())


if __name__ == "__main__":
  unittest.main()