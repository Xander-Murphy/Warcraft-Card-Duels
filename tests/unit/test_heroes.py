import unittest

from hero_data import KORYNE, GENJO, SCATTER, BRAEKS
from lib.types import SpellSchool, TargetType


class TestHeroes(unittest.TestCase):

  def test_heroes_exist(self):
    self.assertEqual(KORYNE.name, "Koryne")
    self.assertEqual(GENJO.name, "Genjo")
    self.assertEqual(SCATTER.name, "Scatter")
    self.assertEqual(BRAEKS.name, "Braeks")

  def test_hero_classes(self):
    self.assertEqual(KORYNE.character_class, "Mage")
    self.assertEqual(GENJO.character_class, "Rogue")
    self.assertEqual(SCATTER.character_class, "Hunter")
    self.assertEqual(BRAEKS.character_class, "Warrior")

  def test_hero_specializations(self):
    self.assertEqual(KORYNE.specialization, "Arcane")
    self.assertEqual(GENJO.specialization, "Subtlety")
    self.assertEqual(SCATTER.specialization, "Survival")
    self.assertEqual(BRAEKS.specialization, "Fury")

  def test_hero_stats(self):
    # (hero, health, attack, defense, speed)
    expected = [
      (KORYNE, 75, 26, 0, 7),
      (GENJO, 85, 23, 1, 9),
      (SCATTER, 95, 21, 2, 7),
      (BRAEKS, 115, 19, 3, 5),
    ]

    for hero, health, attack, defense, speed in expected:
      with self.subTest(hero=hero.name):
        self.assertEqual(hero.health, health)
        self.assertEqual(hero.attack, attack)
        self.assertEqual(hero.defense, defense)
        self.assertEqual(hero.speed, speed)

  def test_heroes_have_abilities(self):
    heroes = [KORYNE, GENJO, SCATTER, BRAEKS]

    for hero in heroes:
      self.assertGreater(len(hero.abilities), 0)

  def test_heroes_have_three_abilities(self):
    heroes = [KORYNE, GENJO, SCATTER, BRAEKS]

    for hero in heroes:
      with self.subTest(hero=hero.name):
        self.assertEqual(len(hero.abilities), 3)

  def test_koryne_arcane_blast(self):
    ability = KORYNE.abilities[0]

    self.assertEqual(ability.name, "Arcane Blast")
    self.assertEqual(ability.school, SpellSchool.ARCANE)
    self.assertEqual(ability.target_type, TargetType.SINGLE_ENEMY)

  def test_koryne_abilities(self):
    ability_names = [ability.name for ability in KORYNE.abilities]

    self.assertIn("Arcane Blast", ability_names)
    self.assertIn("Arcane Explosion", ability_names)
    self.assertIn("Arcane Barrier", ability_names)

  def test_genjo_abilities(self):
    ability_names = [ability.name for ability in GENJO.abilities]

    self.assertIn("Backstab", ability_names)
    self.assertIn("Evasion", ability_names)
    self.assertIn("Cloak of Shadows", ability_names)

  def test_scatter_abilities(self):
    ability_names = [ability.name for ability in SCATTER.abilities]

    self.assertIn("Serpent Sting", ability_names)
    self.assertIn("Multi-Shot", ability_names)
    self.assertIn("Survival Instincts", ability_names)

  def test_braeks_abilities(self):
    ability_names = [ability.name for ability in BRAEKS.abilities]

    self.assertIn("Heroic Strike", ability_names)
    self.assertIn("Berserker Rage", ability_names)
    self.assertIn("Whirlwind", ability_names)


if __name__ == "__main__":
  unittest.main()