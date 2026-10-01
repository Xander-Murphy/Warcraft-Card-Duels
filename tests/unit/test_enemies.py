import unittest

from enemy_data import (
  RAGEFIRE_TROG,
  RAGEFIRE_SHAMAN,
  EARTHBORER,
  MOLTEN_ELEMENTAL
)
from lib.types import SpellSchool, TargetType


class TestEnemies(unittest.TestCase):

  def test_enemies_exist(self):
    self.assertEqual(RAGEFIRE_TROG.name, "Ragefire Trog")
    self.assertEqual(RAGEFIRE_SHAMAN.name, "Ragefire Shaman")
    self.assertEqual(EARTHBORER.name, "Earthborer")
    self.assertEqual(MOLTEN_ELEMENTAL.name, "Molten Elemental")

  def test_enemies_have_abilities(self):
    enemies = [
      RAGEFIRE_TROG,
      RAGEFIRE_SHAMAN,
      EARTHBORER,
      MOLTEN_ELEMENTAL
    ]

    for enemy in enemies:
      self.assertGreater(len(enemy.abilities), 0)

  def test_trog_smash(self):
    ability = RAGEFIRE_TROG.abilities[0]

    self.assertEqual(ability.name, "Trog Smash")
    self.assertEqual(ability.school, SpellSchool.PHYSICAL)
    self.assertEqual(ability.target_type, TargetType.SINGLE_ENEMY)


if __name__ == "__main__":
  unittest.main()