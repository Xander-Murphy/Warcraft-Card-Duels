import subprocess
import sys
import unittest
from pathlib import Path

import combat as combat_module
from abilities import Ability
from ability_effects import ApplyStatusEffect, DamageEffect
from characters import Character
from combat import Combat
from effects_data import PHYSICAL_IMMUNITY, POISON
from enemy_data import DEFIAS_MINER, RAGEFIRE_TROG
from hero_data import BRAEKS, GENJO, KORYNE
from lib.types import SpellSchool, TargetType


def strike(power=20, cooldown=1, priority=0, effects=None):
  return Ability(
    "Strike", "", power, cooldown, TargetType.SINGLE_ENEMY,
    SpellSchool.PHYSICAL, priority,
    effects if effects is not None else [DamageEffect()]
  )


def fighter(name, speed=5, health=100, defense=0, abilities=None):
  return Character(
    name, "Test", health, 0, defense, speed,
    abilities=abilities if abilities is not None else [strike()]
  )


def standard_fight():
  heroes = [KORYNE.clone(), GENJO.clone(), BRAEKS.clone()]
  enemies = [RAGEFIRE_TROG.clone(), DEFIAS_MINER.clone()]
  return Combat(heroes, enemies), heroes, enemies


class TestSetup(unittest.TestCase):

  def test_new_combat_starts_at_round_one_and_is_not_over(self):
    combat, heroes, enemies = standard_fight()

    self.assertEqual(combat.round_number, 1)
    self.assertFalse(combat.is_over())
    self.assertEqual(combat.heroes, heroes)
    self.assertEqual(combat.enemies, enemies)

  def test_living_lists_exclude_the_dead(self):
    combat, heroes, enemies = standard_fight()
    enemies[0].take_damage(10_000)
    heroes[2].take_damage(10_000)

    self.assertEqual(combat.living_enemies(), [enemies[1]])
    self.assertEqual(combat.living_heroes(), [heroes[0], heroes[1]])

  def test_combat_does_not_depend_on_pygame(self):
    # Run in a clean interpreter so other tests importing pygame don't count.
    src = str(Path(combat_module.__file__).parent)
    code = "import combat, sys; sys.exit('pygame' in sys.modules)"

    result = subprocess.run(
      [sys.executable, "-c", code], cwd=src, capture_output=True
    )

    self.assertEqual(result.returncode, 0, result.stderr.decode())


class TestQueueing(unittest.TestCase):

  def test_queue_action_builds_and_stores_the_action(self):
    combat, heroes, enemies = standard_fight()
    ability = heroes[0].abilities[0]

    action = combat.queue_action(heroes[0], ability, [enemies[0]])

    assert action is not None
    self.assertIs(action.actor, heroes[0])
    self.assertIs(combat.action_for(heroes[0]), action)
    self.assertEqual(len(combat.combat_round.action_queue.actions), 1)

  def test_an_actor_can_only_queue_one_action_per_round(self):
    combat, heroes, enemies = standard_fight()
    koryne = heroes[0]

    first = combat.queue_action(koryne, koryne.abilities[0], [enemies[0]])
    second = combat.queue_action(koryne, koryne.abilities[1], enemies)

    self.assertIsNotNone(first)
    self.assertIsNone(second)
    self.assertEqual(len(combat.combat_round.action_queue.actions), 1)

  def test_dead_actor_cannot_queue(self):
    combat, heroes, enemies = standard_fight()
    heroes[0].take_damage(10_000)

    self.assertIsNone(
      combat.queue_action(heroes[0], heroes[0].abilities[0], [enemies[0]])
    )

  def test_ability_on_cooldown_cannot_be_queued(self):
    combat, heroes, enemies = standard_fight()
    heroes[0].abilities[0].use()

    self.assertFalse(combat.can_queue(heroes[0], heroes[0].abilities[0]))

  def test_actor_cannot_queue_an_ability_they_do_not_own(self):
    combat, heroes, enemies = standard_fight()

    self.assertIsNone(
      combat.queue_action(heroes[0], heroes[1].abilities[0], [enemies[0]])
    )

  def test_character_outside_the_fight_cannot_queue(self):
    combat, _, enemies = standard_fight()
    stranger = KORYNE.clone()

    self.assertIsNone(
      combat.queue_action(stranger, stranger.abilities[0], [enemies[0]])
    )

  def test_cannot_queue_with_no_living_target(self):
    combat, heroes, enemies = standard_fight()
    enemies[0].take_damage(10_000)

    self.assertIsNone(
      combat.queue_action(heroes[0], heroes[0].abilities[0], [enemies[0]])
    )

  def test_enemies_queue_through_the_same_rules(self):
    combat, heroes, enemies = standard_fight()
    trog = enemies[0]

    action = combat.queue_action(trog, trog.abilities[0], [heroes[0]])

    assert action is not None
    self.assertIs(action.actor, trog)

  def test_ready_to_resolve_once_every_living_hero_has_orders(self):
    combat, heroes, enemies = standard_fight()
    self.assertFalse(combat.is_ready_to_resolve())
    self.assertEqual(combat.heroes_awaiting_orders(), heroes)

    for hero in heroes[:2]:
      combat.queue_action(hero, hero.abilities[0], [enemies[0]])
    self.assertEqual(combat.heroes_awaiting_orders(), [heroes[2]])
    self.assertFalse(combat.is_ready_to_resolve())

    combat.queue_action(heroes[2], heroes[2].abilities[0], [enemies[0]])
    self.assertTrue(combat.is_ready_to_resolve())

  def test_dead_heroes_are_not_waited_on(self):
    combat, heroes, enemies = standard_fight()
    heroes[2].take_damage(10_000)

    for hero in heroes[:2]:
      combat.queue_action(hero, hero.abilities[0], [enemies[0]])

    self.assertTrue(combat.is_ready_to_resolve())


class TestResolvingActions(unittest.TestCase):

  def test_actions_resolve_fastest_first(self):
    slow, fast = fighter("Slow", speed=2), fighter("Fast", speed=9)
    enemy = fighter("Enemy", health=500)
    combat = Combat([slow, fast], [enemy])
    combat.queue_action(slow, slow.abilities[0], [enemy])
    combat.queue_action(fast, fast.abilities[0], [enemy])

    results = combat.resolve_round()

    self.assertEqual([r.source for r in results], [fast, slow])

  def test_ability_priority_beats_speed(self):
    quick = fighter("Quick", speed=9)
    cautious = fighter(
      "Cautious", speed=1,
      abilities=[strike(priority=10)]
    )
    enemy = fighter("Enemy", health=500)
    combat = Combat([quick, cautious], [enemy])
    combat.queue_action(quick, quick.abilities[0], [enemy])
    combat.queue_action(cautious, cautious.abilities[0], [enemy])

    results = combat.resolve_round()

    self.assertEqual([r.source for r in results], [cautious, quick])

  def test_ties_resolve_in_the_order_they_were_queued(self):
    first, second = fighter("First"), fighter("Second")
    enemy = fighter("Enemy", health=500)
    combat = Combat([first, second], [enemy])
    combat.queue_action(first, first.abilities[0], [enemy])
    combat.queue_action(second, second.abilities[0], [enemy])

    results = combat.resolve_round()

    self.assertEqual([r.source for r in results], [first, second])

  def test_heroes_and_enemies_share_one_turn_order(self):
    hero = fighter("Hero", speed=5)
    enemy = fighter("Enemy", speed=8)
    combat = Combat([hero], [enemy])
    combat.queue_action(hero, hero.abilities[0], [enemy])
    combat.queue_action(enemy, enemy.abilities[0], [hero])

    results = combat.resolve_round()

    self.assertEqual([r.source for r in results], [enemy, hero])

  def test_results_report_what_happened(self):
    hero, enemy = fighter("Hero"), fighter("Enemy")
    combat = Combat([hero], [enemy])
    combat.queue_action(hero, hero.abilities[0], [enemy])

    results = combat.resolve_round()

    self.assertEqual(len(results), 1)
    self.assertEqual(results[0].amount, 20)
    self.assertEqual(enemy.health, 80)

  def test_a_dead_actor_does_not_act(self):
    # The fast enemy kills the slow hero before the hero's turn comes.
    hero = fighter("Hero", speed=1, health=10)
    enemy = fighter("Enemy", speed=9, abilities=[strike(power=50)])
    combat = Combat([hero, fighter("Ally")], [enemy])
    combat.queue_action(hero, hero.abilities[0], [enemy])
    combat.queue_action(enemy, enemy.abilities[0], [hero])

    combat.resolve_round()

    self.assertEqual(hero.health, 0)
    self.assertEqual(enemy.health, 100)
    self.assertTrue(hero.abilities[0].is_ready())

  def test_attack_on_an_already_dead_target_fizzles_without_cooldown(self):
    fast = fighter("Fast", speed=9, abilities=[strike(power=500)])
    slow = fighter("Slow", speed=1, abilities=[strike(cooldown=3)])
    target, other = fighter("Target"), fighter("Other")
    combat = Combat([fast, slow], [target, other])
    combat.queue_action(fast, fast.abilities[0], [target])
    combat.queue_action(slow, slow.abilities[0], [target])

    results = combat.resolve_round()

    self.assertEqual(len(results), 1)
    self.assertTrue(slow.abilities[0].is_ready())

  def test_area_ability_hits_everyone_through_the_real_pipeline(self):
    combat, heroes, enemies = standard_fight()
    braeks = heroes[2]
    combat.queue_action(braeks, braeks.abilities[2], enemies)

    combat.resolve_round()

    self.assertEqual(enemies[0].health, enemies[0].max_health - 18)
    self.assertEqual(enemies[1].health, enemies[1].max_health - 18)

  def test_evasion_protects_for_the_round_then_expires(self):
    hero = fighter(
      "Hero", speed=5,
      abilities=[Ability(
        "Dodge", "", 0, 3, TargetType.SELF, priority=10,
        effects=[ApplyStatusEffect(PHYSICAL_IMMUNITY)]
      )]
    )
    enemy = fighter("Enemy", abilities=[strike(power=30)])
    combat = Combat([hero], [enemy])

    combat.queue_action(hero, hero.abilities[0], [hero])
    combat.queue_action(enemy, enemy.abilities[0], [hero])
    combat.resolve_round()
    self.assertEqual(hero.health, 100)
    self.assertEqual(hero.active_effects, [])

    # Next round the immunity is gone and the enemy connects.
    combat.queue_action(enemy, enemy.abilities[0], [hero])
    combat.resolve_round()
    self.assertEqual(hero.health, 70)


class TestRoundLifecycle(unittest.TestCase):

  def test_round_advances_and_the_queue_is_cleared(self):
    combat, heroes, enemies = standard_fight()
    combat.queue_action(heroes[0], heroes[0].abilities[0], [enemies[0]])

    combat.resolve_round()

    self.assertEqual(combat.round_number, 2)
    self.assertEqual(combat.combat_round.action_queue.actions, [])
    self.assertIsNone(combat.action_for(heroes[0]))

  def test_actors_can_queue_again_next_round(self):
    hero, enemy = fighter("Hero"), fighter("Enemy", health=500)
    combat = Combat([hero], [enemy])

    combat.queue_action(hero, hero.abilities[0], [enemy])
    combat.resolve_round()

    self.assertIsNotNone(
      combat.queue_action(hero, hero.abilities[0], [enemy])
    )

  def test_resolving_an_empty_round_still_advances(self):
    combat, _, _ = standard_fight()

    self.assertEqual(combat.resolve_round(), [])
    self.assertEqual(combat.round_number, 2)

  def test_cooldown_of_one_is_available_every_round(self):
    hero, enemy = fighter("Hero"), fighter("Enemy", health=500)
    combat = Combat([hero], [enemy])

    for _ in range(3):
      self.assertIsNotNone(
        combat.queue_action(hero, hero.abilities[0], [enemy])
      )
      combat.resolve_round()

    self.assertEqual(enemy.health, 500 - 60)

  def test_longer_cooldowns_block_the_ability_for_the_right_rounds(self):
    # Koryne's Arcane Blast has cooldown 2: usable every other round.
    combat, heroes, enemies = standard_fight()
    koryne = heroes[0]
    blast = koryne.abilities[0]
    available = []

    for _ in range(4):
      available.append(combat.can_queue(koryne, blast))
      combat.queue_action(koryne, blast, [enemies[1]])
      combat.resolve_round()

    self.assertEqual(available, [True, False, True, False])

  def test_unused_abilities_still_cool_down(self):
    combat, heroes, _ = standard_fight()
    blast = heroes[0].abilities[0]
    blast.use()  # on cooldown 2

    combat.resolve_round()
    self.assertFalse(blast.is_ready())
    combat.resolve_round()
    self.assertTrue(blast.is_ready())


class TestDamageOverTime(unittest.TestCase):

  def poisoned_fight(self):
    attacker = fighter(
      "Attacker",
      abilities=[strike(power=0, cooldown=9, effects=[ApplyStatusEffect(POISON)])]
    )
    victim = fighter("Victim", health=100, defense=5)
    other = fighter("Bystander", health=500)
    combat = Combat([attacker], [victim, other])
    combat.queue_action(attacker, attacker.abilities[0], [victim])
    return combat, victim

  def test_poison_ticks_each_round_for_its_duration_then_ends(self):
    combat, victim = self.poisoned_fight()
    health = []

    for _ in range(4):
      combat.resolve_round()
      health.append(victim.health)

    # applied in round 1, then 10 nature damage - 5 defense, for 3 rounds
    self.assertEqual(health, [95, 90, 85, 85])
    self.assertEqual(victim.active_effects, [])

  def test_poison_ticks_are_reported_in_the_round_results(self):
    combat, victim = self.poisoned_fight()

    results = combat.resolve_round()

    tick = results[-1]
    self.assertIs(tick.target, victim)
    self.assertEqual(tick.amount, 5)
    self.assertIn("Poison", tick.description)

  def test_poison_is_nature_damage_so_nature_resistance_applies(self):
    combat, victim = self.poisoned_fight()
    victim.resistances[SpellSchool.NATURE] = 100

    combat.resolve_round()

    self.assertEqual(victim.health, 100)

  def test_magical_immunity_blocks_poison_but_physical_immunity_does_not(self):
    from effects_data import MAGICAL_IMMUNITY
    combat, victim = self.poisoned_fight()
    victim.add_effect(MAGICAL_IMMUNITY.clone())
    victim.active_effects[-1].remaining_duration = 5

    combat.resolve_round()
    self.assertEqual(victim.health, 100)

    victim.active_effects = [
      e for e in victim.active_effects if e.name != "Magical Immunity"
    ]
    victim.add_effect(PHYSICAL_IMMUNITY.clone())
    victim.active_effects[-1].remaining_duration = 5

    combat.resolve_round()
    self.assertEqual(victim.health, 95)

  def test_poison_can_kill(self):
    combat, victim = self.poisoned_fight()
    victim.health = 8

    combat.resolve_round()
    combat.resolve_round()

    self.assertFalse(victim.is_alive())
    self.assertEqual(victim.health, 0)

  def test_dead_characters_do_not_tick(self):
    combat, victim = self.poisoned_fight()
    combat.resolve_round()
    victim.take_damage(10_000)

    results = combat.resolve_round()

    self.assertEqual(results, [])


class TestVictoryAndDefeat(unittest.TestCase):

  def test_combat_is_over_when_all_enemies_die(self):
    hero = fighter("Hero", abilities=[strike(power=500)])
    enemy = fighter("Enemy")
    combat = Combat([hero], [enemy])
    combat.queue_action(hero, hero.abilities[0], [enemy])

    combat.resolve_round()

    self.assertTrue(combat.is_over())
    self.assertTrue(combat.living_heroes())
    self.assertFalse(combat.living_enemies())

  def test_combat_is_over_when_all_heroes_die(self):
    hero = fighter("Hero", health=10)
    enemy = fighter("Enemy", abilities=[strike(power=500)])
    combat = Combat([hero], [enemy])
    combat.queue_action(enemy, enemy.abilities[0], [hero])

    combat.resolve_round()

    self.assertTrue(combat.is_over())
    self.assertFalse(combat.living_heroes())

  def test_poison_can_decide_the_fight_at_round_end(self):
    hero = fighter("Hero")
    enemy = fighter("Enemy", health=5)
    enemy.add_effect(POISON.clone())
    combat = Combat([hero], [enemy])

    combat.resolve_round()

    self.assertTrue(combat.is_over())

  def test_nothing_resolves_once_the_fight_is_over(self):
    hero = fighter("Hero", abilities=[strike(power=500)])
    enemy = fighter("Enemy")
    combat = Combat([hero], [enemy])
    combat.queue_action(hero, hero.abilities[0], [enemy])
    combat.resolve_round()
    round_after_victory = combat.round_number

    self.assertEqual(combat.resolve_round(), [])
    self.assertEqual(combat.round_number, round_after_victory)

  def test_cannot_queue_after_the_fight_is_over(self):
    hero = fighter("Hero", abilities=[strike(power=500)])
    enemy = fighter("Enemy")
    combat = Combat([hero], [enemy])
    combat.queue_action(hero, hero.abilities[0], [enemy])
    combat.resolve_round()

    self.assertIsNone(combat.queue_action(hero, hero.abilities[0], [enemy]))

  def test_no_round_end_upkeep_after_the_winning_blow(self):
    # A poisoned survivor must not be finished off by a tick after victory.
    hero = fighter("Hero", health=5, abilities=[strike(power=500)])
    hero.add_effect(POISON.clone())
    enemy = fighter("Enemy")
    combat = Combat([hero], [enemy])
    combat.queue_action(hero, hero.abilities[0], [enemy])

    combat.resolve_round()

    self.assertTrue(hero.is_alive())
    self.assertEqual(combat.round_number, 1)


if __name__ == "__main__":
  unittest.main()
