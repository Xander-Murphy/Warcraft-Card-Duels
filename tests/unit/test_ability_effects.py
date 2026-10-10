import unittest

from abilities import Ability
from ability_effects import (
  AbilityEffect,
  ApplyStatusEffect,
  DamageEffect,
  EffectResult,
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


class TestAbilityEffectContract(unittest.TestCase):

  def test_abstract_effect_cannot_be_instantiated(self):
    with self.assertRaises(TypeError):
      AbilityEffect()

  def test_all_effects_share_the_interface(self):
    for effect in (DamageEffect(), HealEffect()):
      self.assertIsInstance(effect, AbilityEffect)

    status = StatusEffect(
      "S", EffectType.BUFF, EffectCategory.PHYSICAL, 1, 1, stat=Stat.ATTACK
    )
    self.assertIsInstance(ApplyStatusEffect(status), AbilityEffect)

  def test_new_effect_types_work_without_changing_ability(self):
    # Open/Closed: a brand new effect plugs in by subclassing only.
    class ExecuteEffect(AbilityEffect):
      def apply(self, source, target, ability):
        target.health = 0
        return EffectResult(source, target, "executed")

    source, target = make_character("Src"), make_character("Tgt")
    ability = make_ability([ExecuteEffect()])

    results = ability.apply(source, [target])

    self.assertFalse(target.is_alive())
    self.assertEqual(results[0].description, "executed")


class TestDamageEffect(unittest.TestCase):

  def test_damage_scales_with_attack_percentage(self):
    source = make_character(attack=26)
    ability = make_ability([DamageEffect()], power=30)

    self.assertEqual(DamageEffect().calculate_damage(source, ability), 38)

  def test_zero_attack_deals_exactly_the_ability_power(self):
    source, target = make_character(attack=0), make_character()
    ability = make_ability([DamageEffect()], power=20)

    result = DamageEffect().apply(source, target, ability)

    self.assertEqual(result.amount, 20)
    self.assertEqual(target.health, 80)

  def test_damage_respects_target_resistance_and_defense(self):
    source = make_character(attack=0)
    target = make_character(defense=2, resistances={SpellSchool.FIRE: 25})
    ability = make_ability([DamageEffect()], power=20, school=SpellSchool.FIRE)

    result = DamageEffect().apply(source, target, ability)

    self.assertEqual(result.amount, 13)
    self.assertEqual(target.health, 87)

  def test_attack_buff_increases_damage(self):
    source = make_character(attack=0)
    source.add_effect(StatusEffect(
      "Rage", EffectType.BUFF, EffectCategory.PHYSICAL, 10, 3, stat=Stat.ATTACK
    ))
    ability = make_ability([DamageEffect()], power=20)

    self.assertEqual(DamageEffect().calculate_damage(source, ability), 22)

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

  def test_result_reports_source_target_and_amount(self):
    source, target = make_character("Src"), make_character("Tgt")

    result = DamageEffect().apply(source, target, make_ability([DamageEffect()]))

    self.assertIs(result.source, source)
    self.assertIs(result.target, target)
    self.assertIn("Src", result.description)
    self.assertIn("Tgt", result.description)


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

  def test_target_receives_a_clone_not_the_prototype(self):
    target = make_character()

    ApplyStatusEffect(self.status).apply(
      make_character(), target, make_ability([])
    )

    self.assertEqual(len(target.active_effects), 1)
    self.assertIsNot(target.active_effects[0], self.status)
    self.assertEqual(target.active_effects[0].name, "Fortify")

  def test_ticking_one_targets_effect_does_not_affect_another(self):
    first, second = make_character(), make_character()
    effect = ApplyStatusEffect(self.status)
    ability = make_ability([])

    effect.apply(make_character(), first, ability)
    effect.apply(make_character(), second, ability)
    first.update_effects()

    self.assertEqual(first.active_effects[0].remaining_duration, 1)
    self.assertEqual(second.active_effects[0].remaining_duration, 2)
    self.assertEqual(self.status.remaining_duration, 2)

  def test_applied_status_changes_the_targets_stats(self):
    target = make_character(defense=1)

    ApplyStatusEffect(self.status).apply(
      make_character(), target, make_ability([])
    )

    self.assertEqual(target.get_stat(Stat.DEFENSE), 6)


class TestAbilityApply(unittest.TestCase):

  def test_applies_every_effect_in_order(self):
    source, target = make_character(), make_character()
    status = StatusEffect(
      "Mark", EffectType.DEBUFF, EffectCategory.CURSE, 1, 2, stat=Stat.DEFENSE
    )
    ability = make_ability([DamageEffect(), ApplyStatusEffect(status)])

    results = ability.apply(source, [target])

    self.assertEqual(len(results), 2)
    self.assertEqual(target.health, 80)
    self.assertEqual(target.active_effects[0].name, "Mark")

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

  def test_ability_without_effects_does_nothing(self):
    target = make_character()

    self.assertEqual(make_ability([]).apply(make_character(), [target]), [])
    self.assertEqual(target.health, 100)


if __name__ == "__main__":
  unittest.main()
