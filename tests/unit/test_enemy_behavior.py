import random
import unittest

from abilities import Ability
from ability_data.enemy_abilities import BASIC_ATTACK, MOLTEN_BLAST
from ability_effects import DamageEffect, HealEffect
from actions import Action
from characters import Character
from combat import Combat
from enemies import Enemy
from enemy_behavior import EnemyBehavior, RandomBehavior
from enemy_data import (
  DEVIATE_RAVAGER, DEVIATE_GUARDIAN, MOLTEN_ELEMENTAL, RAGEFIRE_TROG
)
from hero_data import BRAEKS, GENJO, KORYNE, SCATTER
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

  def test_every_enemy_has_its_own_basic_attack(self):
    first, second = DEVIATE_RAVAGER.clone(), DEVIATE_RAVAGER.clone()

    self.assertIsNot(first.basic_attack, BASIC_ATTACK)
    self.assertIsNot(first.basic_attack, second.basic_attack)
    self.assertIsNot(first.basic_attack, DEVIATE_RAVAGER.basic_attack)
    self.assertEqual(first.basic_attack.name, "Basic Attack")

  def test_a_newly_built_enemy_does_not_share_the_prototype_basic_attack(self):
    first, second = make_enemy("First"), make_enemy("Second")

    self.assertIsNot(first.basic_attack, BASIC_ATTACK)
    self.assertIsNot(first.basic_attack, second.basic_attack)

  def test_enemies_without_abilities_still_get_a_basic_attack(self):
    self.assertEqual(DEVIATE_RAVAGER.abilities, [])
    self.assertEqual(DEVIATE_RAVAGER.basic_attack.power, 15)

  def test_basic_attack_uses_the_enemys_attack_stat_like_any_damage(self):
    ravager = DEVIATE_RAVAGER.clone()  # attack 11
    hero = make_hero()

    result = DamageEffect().apply(ravager, hero, ravager.basic_attack)

    self.assertEqual(result.amount, 17)  # round(15 * 1.11)

  def test_enemy_owns_its_abilities_and_its_basic_attack_only(self):
    trog, other = RAGEFIRE_TROG.clone(), RAGEFIRE_TROG.clone()
    hero = KORYNE.clone()

    self.assertTrue(trog.has_ability(trog.abilities[0]))
    self.assertTrue(trog.has_ability(trog.basic_attack))
    self.assertFalse(trog.has_ability(other.abilities[0]))
    self.assertFalse(trog.has_ability(other.basic_attack))
    self.assertFalse(trog.has_ability(hero.abilities[0]))

  def test_clone_keeps_ownership_of_its_own_basic_attack(self):
    clone = MOLTEN_ELEMENTAL.clone()

    self.assertTrue(clone.has_ability(clone.basic_attack))
    self.assertFalse(clone.has_ability(MOLTEN_ELEMENTAL.basic_attack))

  def test_heroes_only_own_their_listed_abilities(self):
    hero = KORYNE.clone()

    self.assertTrue(hero.has_ability(hero.abilities[0]))
    self.assertFalse(hero.has_ability(BASIC_ATTACK))


class TestRandomBehavior(unittest.TestCase):

  def setUp(self):
    self.heroes = [make_hero("A"), make_hero("B"), make_hero("C")]

  def choose(self, enemy, rng=None):
    behavior = RandomBehavior(random.Random(rng) if rng is not None else None)
    return behavior.choose_action(
      enemy, Battlefield(self.heroes, [enemy])
    )

  def test_enemy_with_no_abilities_uses_its_basic_attack(self):
    enemy = make_enemy()
    action = self.choose(enemy, rng=1)

    assert action is not None
    self.assertIs(action.ability, enemy.basic_attack)
    self.assertIs(action.actor, enemy)

  def test_enemy_uses_a_ready_ability_in_preference_to_the_basic_attack(self):
    smash = make_ability("Smash")
    enemy = make_enemy(abilities=[smash])

    for seed in range(20):
      action = self.choose(enemy, rng=seed)
      assert action is not None
      self.assertIs(action.ability, smash)

  def test_enemy_uses_basic_attack_when_every_ability_is_on_cooldown(self):
    smash = make_ability("Smash", cooldown=3)
    enemy = make_enemy(abilities=[smash])
    smash.use()

    action = self.choose(enemy, rng=1)

    assert action is not None
    self.assertIs(action.ability, enemy.basic_attack)

  def test_on_cooldown_abilities_are_never_chosen(self):
    ready = make_ability("Ready")
    cooling = make_ability("Cooling", cooldown=3)
    enemy = make_enemy(abilities=[cooling, ready])
    cooling.use()

    for seed in range(30):
      action = self.choose(enemy, rng=seed)
      assert action is not None
      self.assertIs(action.ability, ready)

  def test_ability_choice_is_random_among_ready_abilities(self):
    first, second = make_ability("First"), make_ability("Second")
    enemy = make_enemy(abilities=[first, second])

    chosen = set()
    for seed in range(40):
      action = self.choose(enemy, rng=seed)
      assert action is not None
      chosen.add(action.ability.name)

    self.assertEqual(chosen, {"First", "Second"})

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

  def test_same_seed_gives_the_same_choice(self):
    enemy = make_enemy(abilities=[make_ability("X"), make_ability("Y")])

    first = self.choose(enemy, rng=7)
    second = self.choose(enemy, rng=7)

    assert first is not None and second is not None
    self.assertEqual(first.ability.name, second.ability.name)
    self.assertEqual(first.targets, second.targets)

  def test_default_behavior_uses_the_shared_random_module(self):
    enemy = make_enemy()

    random.seed(11)
    first = RandomBehavior().choose_action(
      enemy, Battlefield(self.heroes, [enemy])
    )
    random.seed(11)
    second = RandomBehavior().choose_action(
      enemy, Battlefield(self.heroes, [enemy])
    )

    assert first is not None and second is not None
    self.assertEqual(first.targets, second.targets)

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

  def test_ally_ability_targets_a_living_enemy_ally(self):
    mend = Ability(
      "Mend", "", 10, 2, TargetType.SINGLE_ALLY, effects=[HealEffect()]
    )
    enemy = make_enemy("Healer", abilities=[mend])
    friend = make_enemy("Friend")
    battlefield = Battlefield(self.heroes, [enemy, friend])
    friend.take_damage(10_000)

    action = RandomBehavior(random.Random(1)).choose_action(enemy, battlefield)

    assert action is not None
    self.assertEqual(action.targets, [enemy])

  def test_no_valid_target_means_no_action(self):
    enemy = make_enemy()
    for hero in self.heroes:
      hero.take_damage(10_000)

    self.assertIsNone(self.choose(enemy, rng=1))


class TestBehaviorIsAStrategy(unittest.TestCase):

  def test_abstract_behavior_cannot_be_instantiated(self):
    with self.assertRaises(TypeError):
      EnemyBehavior()  # pyright: ignore[reportAbstractUsage]

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

  def test_behavior_that_has_no_move_queues_nothing(self):
    class Passive(EnemyBehavior):
      def choose_action(self, enemy, battlefield):
        return None

    combat = Combat([make_hero()], [make_enemy(behavior=Passive())])

    self.assertEqual(combat.plan_enemy_actions(), [])

  def test_default_enemy_behavior_is_random(self):
    self.assertIsInstance(make_enemy().behavior, RandomBehavior)

  def test_each_enemy_has_its_own_behavior_object(self):
    self.assertIsNot(
      DEVIATE_RAVAGER.clone().behavior, DEVIATE_RAVAGER.clone().behavior
    )


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

  def test_enemies_with_no_abilities_can_now_act(self):
    ravager = seeded(DEVIATE_RAVAGER.clone())
    combat = Combat(party(), [ravager])

    planned = combat.plan_enemy_actions()

    self.assertIs(planned[0].ability, ravager.basic_attack)

  def test_dead_enemies_are_skipped(self):
    alive, dead = seeded(RAGEFIRE_TROG.clone()), seeded(RAGEFIRE_TROG.clone())
    dead.take_damage(10_000)
    combat = Combat(party(), [alive, dead])

    planned = combat.plan_enemy_actions()

    self.assertEqual([a.actor for a in planned], [alive])

  def test_enemies_that_already_have_orders_are_left_alone(self):
    trog = seeded(RAGEFIRE_TROG.clone())
    heroes = party()
    combat = Combat(heroes, [trog])
    manual = combat.queue_action(trog, trog.basic_attack, [heroes[0]])

    planned = combat.plan_enemy_actions()

    self.assertEqual(planned, [])
    self.assertIs(combat.action_for(trog), manual)

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

  def test_planning_twice_does_not_double_up(self):
    combat = Combat(party(), [seeded(RAGEFIRE_TROG.clone())])

    combat.plan_enemy_actions()
    combat.plan_enemy_actions()

    self.assertEqual(len(combat.combat_round.action_queue.actions), 1)

  def test_nothing_is_planned_once_the_fight_is_over(self):
    heroes = party()
    for hero in heroes:
      hero.take_damage(10_000)
    combat = Combat(heroes, [seeded(RAGEFIRE_TROG.clone())])

    self.assertEqual(combat.plan_enemy_actions(), [])

  def test_heroes_and_enemies_share_the_same_queue_and_turn_order(self):
    heroes = party()
    trog = seeded(RAGEFIRE_TROG.clone())  # speed 4
    combat = Combat(heroes, [trog])
    combat.queue_action(heroes[1], heroes[1].abilities[0], [trog])  # Genjo
    combat.plan_enemy_actions()

    combat.combat_round.prepare()
    order = [a.actor for a in combat.combat_round.action_queue.actions]

    self.assertEqual(order[0], heroes[1])
    self.assertIn(trog, order)

  def test_planned_enemy_attacks_really_hurt_heroes(self):
    heroes = party()
    ravager = seeded(DEVIATE_RAVAGER.clone())
    combat = Combat(heroes, [ravager])
    combat.plan_enemy_actions()

    results = combat.resolve_round()

    self.assertEqual(len(results), 1)
    self.assertGreater(results[0].amount, 0)
    self.assertEqual(
      sum(hero.max_health - hero.health for hero in heroes),
      results[0].amount
    )

  def test_enemy_alternates_special_and_basic_attack_around_its_cooldown(self):
    # Molten Blast has cooldown 2: blast, basic, blast, basic ...
    molten = seeded(MOLTEN_ELEMENTAL.clone())
    hero = Character("Target", "Test", 1000, 0, 0, 5)
    combat = Combat([hero], [molten])
    used = []

    for _ in range(4):
      combat.plan_enemy_actions()
      results = combat.resolve_round()
      used.append(
        "blast" if MOLTEN_BLAST.name in results[0].description else "basic"
      )

    self.assertEqual(used, ["blast", "basic", "blast", "basic"])

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

  def test_the_same_seed_always_plays_out_the_same_way(self):
    first, heroes_a, _ = self.play(4)
    second, heroes_b, _ = self.play(4)

    self.assertEqual(first.round_number, second.round_number)
    self.assertEqual(
      [h.health for h in heroes_a], [h.health for h in heroes_b]
    )


if __name__ == "__main__":
  unittest.main()
