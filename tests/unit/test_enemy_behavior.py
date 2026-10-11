import random
import unittest

from abilities import Ability
from ability_data.common_abilities import BASIC_ATTACK
from ability_effects import DamageEffect, HealEffect
from actions import Action
from characters import Character
from combat import Combat
from enemies import Enemy
from enemy_behavior import EnemyBehavior, RandomBehavior
from enemy_data import RAGEFIRE_TROG
from hero_data import KORYNE
from lib.types import SpellSchool, TargetType
from targeting import Battlefield, resolver_for


def make_hero(name="Hero", health=100, defense=0):
  return Character(name, "Test", health, 0, defense, 5)


def make_ability(name, target_type=TargetType.SINGLE_ENEMY, cooldown=1):
  return Ability(
    name, "", 10, cooldown, target_type, SpellSchool.PHYSICAL,
    effects=[DamageEffect()]
  )


def make_enemy(name="Enemy", abilities=None, **kwargs):
  return Enemy(name, "Test", 50, 0, 0, 5, abilities=abilities, **kwargs)


class TestBasicAttack(unittest.TestCase):

  def test_basic_attack_is_flat_15_physical_damage_with_no_cooldown(self):
    self.assertEqual(BASIC_ATTACK.power, 15)
    self.assertEqual(BASIC_ATTACK.cooldown, 0)
    self.assertEqual(BASIC_ATTACK.school, SpellSchool.PHYSICAL)
    self.assertEqual(BASIC_ATTACK.target_type, TargetType.SINGLE_ENEMY)
    self.assertTrue(
      any(isinstance(e, DamageEffect) for e in BASIC_ATTACK.effects)
    )

  def test_basic_attack_is_always_ready(self):
    attack = BASIC_ATTACK.clone()

    for _ in range(3):
      self.assertTrue(attack.is_ready())
      attack.use()
      attack.reduce_cooldown()

    self.assertTrue(attack.is_ready())

  def test_enemy_can_always_use_its_basic_attack_but_only_ready_abilities(self):
    trog, other = RAGEFIRE_TROG.clone(), RAGEFIRE_TROG.clone()
    smash = trog.abilities[0]  # cooldown 1

    self.assertTrue(trog.can_use(smash))
    self.assertTrue(trog.can_use(trog.basic_attack))

    smash.use()

    self.assertFalse(trog.can_use(smash))
    self.assertTrue(trog.can_use(trog.basic_attack))
    self.assertFalse(trog.can_use(other.abilities[0]))
    self.assertFalse(trog.can_use(other.basic_attack))
    self.assertFalse(trog.can_use(KORYNE.clone().abilities[0]))


class TestRandomBehavior(unittest.TestCase):

  def setUp(self):
    self.heroes = [make_hero("A"), make_hero("B"), make_hero("C")]

  def choose(self, enemy, rng=None):
    behavior = RandomBehavior(random.Random(rng) if rng is not None else None)
    return behavior.choose_action(
      enemy, Battlefield(self.heroes, [enemy])
    )

  def test_ability_and_basic_attack_are_roughly_equally_likely(self):
    smash = make_ability("Smash")
    enemy = make_enemy(abilities=[smash])

    smashes = sum(
      1 for seed in range(400)
      if (action := self.choose(enemy, rng=seed)) is not None
      and action.ability is smash
    )

    self.assertGreater(smashes, 150)
    self.assertLess(smashes, 250)

  def test_enemy_uses_basic_attack_when_every_ability_is_on_cooldown(self):
    smash = make_ability("Smash", cooldown=3)
    enemy = make_enemy(abilities=[smash])
    smash.use()

    action = self.choose(enemy, rng=1)

    assert action is not None
    self.assertIs(action.ability, enemy.basic_attack)

  def test_ability_choice_is_random_among_ready_abilities(self):
    first, second = make_ability("First"), make_ability("Second")
    enemy = make_enemy(abilities=[first, second])

    chosen = set()
    for seed in range(40):
      action = self.choose(enemy, rng=seed)
      assert action is not None
      chosen.add(action.ability.name)

    self.assertEqual(chosen, {"First", "Second", "Basic Attack"})

  def test_single_target_is_a_random_living_hero(self):
    enemy = make_enemy()

    targeted = set()
    for seed in range(60):
      action = self.choose(enemy, rng=seed)
      assert action is not None
      self.assertEqual(len(action.targets), 1)
      targeted.add(action.targets[0].name)

    self.assertEqual(targeted, {"A", "B", "C"})

  def test_dead_heroes_are_never_targeted(self):
    enemy = make_enemy()
    self.heroes[1].take_damage(10_000)

    for seed in range(60):
      action = self.choose(enemy, rng=seed)
      assert action is not None
      self.assertNotEqual(action.targets[0].name, "B")

  def test_area_ability_targets_every_living_hero(self):
    sweep = make_ability("Sweep", TargetType.ALL_ENEMIES)
    enemy = make_enemy(abilities=[sweep])
    self.heroes[2].take_damage(10_000)

    action = self.choose(enemy, rng=1)

    assert action is not None
    self.assertEqual(action.targets, self.heroes[:2])

  def test_self_ability_targets_the_enemy_itself(self):
    mend = Ability(
      "Mend", "", 10, 2, TargetType.SELF, effects=[HealEffect()]
    )
    enemy = make_enemy(abilities=[mend])

    action = self.choose(enemy, rng=1)

    assert action is not None
    self.assertEqual(action.targets, [enemy])

  def test_no_valid_target_means_no_action(self):
    enemy = make_enemy()
    for hero in self.heroes:
      hero.take_damage(10_000)

    self.assertIsNone(self.choose(enemy, rng=1))


class TestBehaviorIsAStrategy(unittest.TestCase):

  def test_new_behavior_plugs_in_without_changing_enemy_or_combat(self):
    # Open/Closed: an enemy that always goes for the weakest hero.
    class FocusWeakest(EnemyBehavior):
      def choose_action(self, enemy, battlefield):
        living = resolver_for(TargetType.SINGLE_ENEMY).candidates(
          enemy, battlefield
        )
        weakest = min(living, key=lambda hero: hero.health)
        return Action(enemy, enemy.basic_attack, [weakest])

    heroes = [make_hero("Tank", 200), make_hero("Squishy", 30)]
    enemy = make_enemy(behavior=FocusWeakest())
    combat = Combat(heroes, [enemy])

    planned = combat.plan_enemy_actions()

    self.assertEqual(planned[0].targets, [heroes[1]])


if __name__ == "__main__":
  unittest.main()
