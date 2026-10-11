import random
import unittest

from encounters import generate_encounter
from enemy_data import DEVIATE_RAVAGER
from game import Game
from hero_data import KORYNE, BRAEKS


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

  # Guards the shared-prototype bug: encounters must hand out copies, never the prototypes.
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

  # Guards the shared-prototype bug: the party must be copies, or damage leaks between runs.
  def test_start_run_builds_party_from_clones(self):
    game = Game(None)
    game.selected_heroes = [KORYNE, BRAEKS]
    game.current_encounter = 2

    game.start_run()

    self.assertEqual([hero.name for hero in game.party], ["Koryne", "Braeks"])
    self.assertIsNot(game.party[0], KORYNE)
    self.assertIsNot(game.party[1], BRAEKS)
    self.assertEqual(game.current_encounter, 0)

  # Guards the shared-prototype bug: a hero defeated in one run must not stay defeated in the next.
  def test_new_run_restores_a_defeated_heroes_health(self):
    game = Game(None)
    game.selected_heroes = [KORYNE]

    game.start_run()
    game.party[0].take_damage(1000)
    self.assertFalse(game.party[0].is_alive())

    game.start_run()
    self.assertTrue(game.party[0].is_alive())
    self.assertEqual(game.party[0].health, KORYNE.max_health)
