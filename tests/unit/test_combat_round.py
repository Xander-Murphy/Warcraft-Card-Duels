import unittest

from actions import Action
from combat_round import CombatRound
from hero_data import KORYNE, GENJO, BRAEKS
from enemy_data import RAGEFIRE_TROG
from ability_data.hero_abilities import (
  ARCANE_BLAST,
  CLOAK_OF_SHADOWS,
  HEROIC_STRIKE
)


class TestCombatRound(unittest.TestCase):

  def test_add_action(self):
    combat_round = CombatRound()

    action = Action(
      KORYNE,
      ARCANE_BLAST,
      [RAGEFIRE_TROG]
    )

    combat_round.add_action(action)

    self.assertEqual(len(combat_round.action_queue.actions), 1)
    self.assertEqual(combat_round.action_queue.actions[0], action)


  def test_prepare_sorts_actions(self):
    combat_round = CombatRound()

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

    combat_round.add_action(koryne_action)
    combat_round.add_action(genjo_action)
    combat_round.add_action(braeks_action)

    combat_round.prepare()

    self.assertEqual(
      combat_round.action_queue.actions[0],
      genjo_action
    )

    self.assertEqual(
      combat_round.action_queue.actions[1],
      koryne_action
    )

    self.assertEqual(
      combat_round.action_queue.actions[2],
      braeks_action
    )


  def test_empty_round(self):
    combat_round = CombatRound()

    self.assertEqual(
      len(combat_round.action_queue.actions),
      0
    )


if __name__ == "__main__":
  unittest.main()