import random
import unittest

from ability_data.enemy_abilities import MOLTEN_BLAST
from actions import Action
from characters import Character
from combat import Combat
from enemies import Enemy
from enemy_behavior import EnemyBehavior, RandomBehavior
from enemy_data import (
  DEVIATE_RAVAGER, DEVIATE_GUARDIAN, MOLTEN_ELEMENTAL, RAGEFIRE_TROG
)
from hero_data import BRAEKS, GENJO, KORYNE, SCATTER
from targeting import resolver_for


def make_enemy(name="Enemy", abilities=None, **kwargs):
  return Enemy(name, "Test", 50, 0, 0, 5, abilities=abilities, **kwargs)


def party():
  return [KORYNE.clone(), GENJO.clone(), BRAEKS.clone()]


def seeded(enemy, seed=0):
  enemy.behavior = RandomBehavior(random.Random(seed))
  return enemy


class TestPlanEnemyActions(unittest.TestCase):

  def test_every_living_enemy_gets_one_action(self):
    enemies = [seeded(DEVIATE_RAVAGER.clone()), seeded(RAGEFIRE_TROG.clone())]
    combat = Combat(party(), enemies)

    planned = combat.plan_enemy_actions()

    self.assertEqual([a.actor for a in planned], enemies)
    for enemy in enemies:
      self.assertIsNotNone(combat.action_for(enemy))

  def test_behavior_is_only_consulted_for_enemies_that_need_orders(self):
    class Spy(EnemyBehavior):
      def __init__(self):
        self.calls = 0

      def choose_action(self, enemy, battlefield):
        self.calls += 1
        return Action(enemy, enemy.basic_attack, battlefield.heroes[:1])

    heroes = party()
    needs_spy, has_spy, dead_spy = Spy(), Spy(), Spy()
    needs_orders = make_enemy("Needs", behavior=needs_spy)
    has_orders = make_enemy("Has", behavior=has_spy)
    dead = make_enemy("Dead", behavior=dead_spy)
    dead.take_damage(10_000)
    combat = Combat(heroes, [needs_orders, has_orders, dead])
    combat.queue_action(has_orders, has_orders.basic_attack, heroes[:1])

    combat.plan_enemy_actions()

    self.assertEqual(needs_spy.calls, 1)
    self.assertEqual(has_spy.calls, 0)
    self.assertEqual(dead_spy.calls, 0)

  def test_a_special_ability_is_never_used_two_rounds_running_while_it_cools_down(self):
    # Molten Blast has cooldown 2, so it can't be chosen the round after use.
    used_blast, used_basic = 0, 0

    for seed in range(12):
      molten = seeded(MOLTEN_ELEMENTAL.clone(), seed)
      hero = Character("Target", "Test", 10_000, 0, 0, 5)
      combat = Combat([hero], [molten])
      previous = None

      for _ in range(8):
        combat.plan_enemy_actions()
        results = combat.resolve_round()
        current = "blast" if MOLTEN_BLAST.name in results[0].description else "basic"
        self.assertFalse(previous == "blast" and current == "blast")
        used_blast += current == "blast"
        used_basic += current == "basic"
        previous = current

    self.assertGreater(used_blast, 0)
    self.assertGreater(used_basic, 0)

  def test_basic_attack_is_available_every_single_round(self):
    ravager = seeded(DEVIATE_RAVAGER.clone())
    hero = Character("Target", "Test", 1000, 0, 0, 5)
    combat = Combat([hero], [ravager])

    for _ in range(5):
      self.assertEqual(len(combat.plan_enemy_actions()), 1)
      combat.resolve_round()

    self.assertEqual(hero.health, 1000 - 5 * 17)


class TestFullFights(unittest.TestCase):
  """Heroes versus Wailing Caverns enemies that have no abilities of their own."""

  def play(self, seed):
    rng = random.Random(seed)
    enemies = [
      seeded(DEVIATE_RAVAGER.clone(), seed),
      seeded(DEVIATE_GUARDIAN.clone(), seed + 1),
      seeded(DEVIATE_RAVAGER.clone(), seed + 2),
    ]
    heroes = [KORYNE.clone(), SCATTER.clone(), BRAEKS.clone()]
    combat = Combat(heroes, enemies)

    while not combat.is_over() and combat.round_number <= 40:
      for hero in combat.living_heroes():
        for ability in hero.abilities:
          if not combat.can_queue(hero, ability):
            continue

          resolver = resolver_for(ability.target_type)
          candidates = resolver.candidates(hero, combat.battlefield)
          choice = rng.randrange(len(candidates)) if candidates else 0
          targets = resolver.resolve(hero, combat.battlefield, choice)

          if combat.queue_action(hero, ability, targets):
            break

      combat.plan_enemy_actions()
      combat.resolve_round()

    return combat, heroes, enemies

  def test_enemies_deal_damage_and_every_fight_reaches_a_conclusion(self):
    for seed in range(15):
      with self.subTest(seed=seed):
        combat, heroes, enemies = self.play(seed)

        self.assertTrue(combat.is_over())
        self.assertLessEqual(combat.round_number, 40)
        damage_taken = sum(h.max_health - h.health for h in heroes)
        self.assertGreater(damage_taken, 0)
