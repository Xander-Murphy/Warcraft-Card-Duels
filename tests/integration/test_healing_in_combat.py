import random
import unittest

from combat import Combat
from combat_controller import CombatController
from enemy_behavior import RandomBehavior
from enemy_data import DEFIAS_MINER
from hero_data import BRAEKS, LIORA, TAMARU, TORVALD, VESK
from targeting import resolver_for


def enemies(count=2):
  spawned = []
  for seed in range(count):
    enemy = DEFIAS_MINER.clone()
    enemy.behavior = RandomBehavior(random.Random(seed))
    spawned.append(enemy)
  return spawned


class TestHealingInCombat(unittest.TestCase):

  def test_the_heal_is_reported_in_the_round_log(self):
    liora, braeks = LIORA.clone(), BRAEKS.clone()
    braeks.take_damage(60)
    combat = Combat([liora, braeks], enemies())

    combat.queue_action(liora, liora.abilities[0], [braeks])
    combat.queue_action(braeks, braeks.basic_attack, [combat.enemies[0]])
    log = [result.description for result in combat.resolve_round()]

    self.assertIn(f"Liora's Flash Heal heals Braeks for {round(30 * 1.18)}", log)

  def test_a_defeated_hero_cannot_be_chosen_for_a_heal(self):
    liora, braeks, torvald = LIORA.clone(), BRAEKS.clone(), TORVALD.clone()
    braeks.take_damage(10_000)
    combat = Combat([liora, braeks, torvald], enemies())
    controller = CombatController(combat)

    controller.confirm()          # Liora's abilities
    controller.confirm()          # Flash Heal -> choose a target

    self.assertNotIn(braeks, controller.target_candidates())

  def test_prayer_of_healing_skips_the_defeated(self):
    liora, braeks, torvald = LIORA.clone(), BRAEKS.clone(), TORVALD.clone()
    torvald.take_damage(50)
    braeks.take_damage(10_000)
    combat = Combat([liora, braeks, torvald], enemies())
    prayer = liora.abilities[1]

    targets = resolver_for(prayer.target_type).resolve(liora, combat.battlefield)
    combat.queue_action(liora, prayer, targets)
    combat.queue_action(torvald, torvald.basic_attack, [combat.enemies[0]])
    log = [result.description for result in combat.resolve_round()]

    self.assertEqual(targets, [liora, torvald])
    self.assertFalse(braeks.is_alive())
    self.assertFalse(any("heals Braeks" in line for line in log))


class TestNewHeroesFight(unittest.TestCase):

  def test_a_party_of_new_heroes_can_finish_a_fight(self):
    for seed in range(5):
      with self.subTest(seed=seed):
        rng = random.Random(seed)
        heroes = [LIORA.clone(), VESK.clone(), TAMARU.clone()]
        combat = Combat(heroes, enemies(3))

        while not combat.is_over() and combat.round_number <= 40:
          for hero in combat.living_heroes():
            options = [a for a in hero.usable_abilities() if combat.can_queue(hero, a)]
            for ability in rng.sample(options, len(options)):
              resolver = resolver_for(ability.target_type)
              candidates = resolver.candidates(hero, combat.battlefield)
              choice = rng.randrange(len(candidates)) if candidates else 0
              targets = resolver.resolve(hero, combat.battlefield, choice)
              if combat.queue_action(hero, ability, targets):
                break
          combat.plan_enemy_actions()
          combat.resolve_round()

        self.assertTrue(combat.is_over())
