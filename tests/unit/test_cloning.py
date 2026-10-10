import random
import unittest

from effects_data import POISON
from encounters import generate_encounter
from enemy_data import DEVIATE_RAVAGER, RAGEFIRE_TROG
from game import Game
from hero_data import KORYNE, BRAEKS


class TestCloning(unittest.TestCase):

  def test_clone_is_a_separate_object_with_the_same_stats(self):
    clone = KORYNE.clone()

    self.assertIsNot(clone, KORYNE)
    self.assertEqual(clone.name, KORYNE.name)
    self.assertEqual(clone.health, KORYNE.health)
    self.assertEqual(clone.specialization, KORYNE.specialization)

  def test_clone_is_the_same_subclass(self):
    self.assertIs(type(KORYNE.clone()), type(KORYNE))
    self.assertIs(type(RAGEFIRE_TROG.clone()), type(RAGEFIRE_TROG))

  def test_damaging_a_clone_does_not_touch_the_prototype_or_siblings(self):
    first = DEVIATE_RAVAGER.clone()
    second = DEVIATE_RAVAGER.clone()

    first.take_damage(20)

    self.assertLess(first.health, DEVIATE_RAVAGER.max_health)
    self.assertEqual(second.health, DEVIATE_RAVAGER.max_health)
    self.assertEqual(DEVIATE_RAVAGER.health, DEVIATE_RAVAGER.max_health)

  def test_cloned_abilities_have_independent_cooldowns(self):
    first = KORYNE.clone()
    second = KORYNE.clone()

    first.abilities[0].use()

    self.assertFalse(first.abilities[0].is_ready())
    self.assertTrue(second.abilities[0].is_ready())
    self.assertTrue(KORYNE.abilities[0].is_ready())

  def test_cloned_abilities_are_not_the_prototype_abilities(self):
    clone = BRAEKS.clone()

    for original, copied in zip(BRAEKS.abilities, clone.abilities):
      with self.subTest(ability=original.name):
        self.assertIsNot(original, copied)
        self.assertIsNot(original.effects, copied.effects)

  def test_cloned_characters_have_independent_resistances_and_effects(self):
    clone = KORYNE.clone()
    clone.resistances[list(clone.resistances)[0]] = 99
    clone.add_effect(POISON.clone())

    self.assertNotEqual(clone.resistances, KORYNE.resistances)
    self.assertEqual(KORYNE.active_effects, [])

  def test_status_effect_clone_has_independent_duration(self):
    clone = POISON.clone()
    clone.reduce_duration()

    self.assertEqual(clone.remaining_duration, POISON.duration - 1)
    self.assertEqual(POISON.remaining_duration, POISON.duration)


class TestEncounterCloning(unittest.TestCase):

  def test_encounter_enemies_are_distinct_objects(self):
    # Wailing Caverns encounter 1 lists DEVIATE_RAVAGER twice, so duplicates
    # are likely. No two enemies may be the same object, and none may be a
    # prototype.
    for seed in range(50):
      random.seed(seed)
      enemies = generate_encounter("Wailing Caverns", 1)

      with self.subTest(seed=seed):
        self.assertEqual(len({id(enemy) for enemy in enemies}), len(enemies))

  def test_encounter_enemies_are_not_prototypes(self):
    from enemy_data import DEVIATE_GUARDIAN

    for seed in range(50):
      random.seed(seed)
      for enemy in generate_encounter("Wailing Caverns", 1):
        self.assertIsNot(enemy, DEVIATE_RAVAGER)
        self.assertIsNot(enemy, DEVIATE_GUARDIAN)

  def test_hitting_one_duplicate_enemy_leaves_the_other_alone(self):
    for seed in range(50):
      random.seed(seed)
      ravagers = [
        enemy for enemy in generate_encounter("Wailing Caverns", 1)
        if enemy.name == "Deviate Ravager"
      ]

      if len(ravagers) >= 2:
        ravagers[0].take_damage(30)
        self.assertEqual(ravagers[1].health, ravagers[1].max_health)
        return

    self.fail("never rolled two Deviate Ravagers in 50 seeds")


class TestGameRun(unittest.TestCase):

  def test_start_run_builds_party_from_clones(self):
    game = Game(None)
    game.selected_heroes = [KORYNE, BRAEKS]
    game.current_encounter = 2

    game.start_run()

    self.assertEqual([hero.name for hero in game.party], ["Koryne", "Braeks"])
    self.assertIsNot(game.party[0], KORYNE)
    self.assertIsNot(game.party[1], BRAEKS)
    self.assertEqual(game.current_encounter, 0)

  def test_new_run_restores_a_defeated_heroes_health(self):
    game = Game(None)
    game.selected_heroes = [KORYNE]

    game.start_run()
    game.party[0].take_damage(1000)
    self.assertFalse(game.party[0].is_alive())

    game.start_run()
    self.assertTrue(game.party[0].is_alive())
    self.assertEqual(game.party[0].health, KORYNE.max_health)

  def test_start_run_does_not_change_selection(self):
    game = Game(None)
    game.selected_heroes = [KORYNE]

    game.start_run()

    self.assertIs(game.selected_heroes[0], KORYNE)


if __name__ == "__main__":
  unittest.main()
