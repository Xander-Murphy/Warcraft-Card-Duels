import unittest

from abilities import Ability
from ability_effects import (
  ApplyStatusEffect,
  DamageEffect,
  HealEffect,
)
from characters import Character
from effects import StatusEffect
from lib.types import EffectCategory, EffectType, SpellSchool, Stat, TargetType


def make_character(name="Dummy", **overrides):
  stats = dict(
    name=name, character_class="Test",
    health=100, attack=0, defense=0, speed=5
  )
  stats.update(overrides)
  return Character(**stats)


def make_ability(effects, power=20, school=SpellSchool.FIRE, **kwargs):
  return Ability(
    "Test Ability", "", power, 1, TargetType.SINGLE_ENEMY, school,
    effects=effects, **kwargs
  )


class TestDamageEffect(unittest.TestCase):

  def test_damage_scales_with_attack_percentage(self):
    source = make_character(attack=26)
    ability = make_ability([DamageEffect()], power=30)

    self.assertEqual(DamageEffect().calculate_damage(source, ability), 38)

  def test_damage_respects_target_resistance_and_defense(self):
    source = make_character(attack=0)
    target = make_character(defense=2, resistances={SpellSchool.FIRE: 25})
    ability = make_ability([DamageEffect()], power=20, school=SpellSchool.FIRE)

    result = DamageEffect().apply(source, target, ability)

    self.assertEqual(result.amount, 13)
    self.assertEqual(target.health, 87)

  def test_immune_target_takes_nothing_and_result_says_so(self):
    source, target = make_character(), make_character("Tgt")
    target.add_effect(StatusEffect(
      "Immune", EffectType.IMMUNITY, EffectCategory.MAGICAL,
      0, 1, [SpellSchool.FIRE]
    ))

    result = DamageEffect().apply(source, target, make_ability([DamageEffect()]))

    self.assertEqual(result.amount, 0)
    self.assertEqual(target.health, 100)
    self.assertIn("immune", result.description)


class TestHealEffect(unittest.TestCase):

  def test_heal_uses_ability_power_and_caps_at_max(self):
    source, target = make_character(), make_character()
    target.take_damage(30)
    ability = make_ability([HealEffect()], power=50, school=SpellSchool.HOLY)

    result = HealEffect().apply(source, target, ability)

    self.assertEqual(result.amount, 30)
    self.assertEqual(target.health, 100)


class TestApplyStatusEffect(unittest.TestCase):

  def setUp(self):
    self.status = StatusEffect(
      "Fortify", EffectType.BUFF, EffectCategory.PHYSICAL,
      5, 2, stat=Stat.DEFENSE
    )


class TestAbilityApply(unittest.TestCase):

  def test_applies_to_every_target(self):
    targets = [make_character(f"T{i}") for i in range(3)]
    ability = make_ability([DamageEffect()])

    results = ability.apply(make_character(), targets)

    self.assertEqual(len(results), 3)
    self.assertTrue(all(target.health == 80 for target in targets))

  def test_dead_targets_are_skipped(self):
    alive, dead = make_character("Alive"), make_character("Dead")
    dead.take_damage(1000)
    ability = make_ability([DamageEffect()])

    results = ability.apply(make_character(), [dead, alive])

    self.assertEqual([r.target for r in results], [alive])

  def test_remaining_effects_stop_once_the_target_dies(self):
    target = make_character(health=10)
    status = StatusEffect(
      "Mark", EffectType.DEBUFF, EffectCategory.CURSE, 1, 2, stat=Stat.DEFENSE
    )
    ability = make_ability([DamageEffect(), ApplyStatusEffect(status)])

    results = ability.apply(make_character(), [target])

    self.assertEqual(len(results), 1)
    self.assertEqual(target.active_effects, [])


if __name__ == "__main__":
  unittest.main()
