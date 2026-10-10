import unittest

from characters import Character
from effects import StatusEffect
from lib.types import EffectCategory, EffectType, SpellSchool, Stat


def make_character(**overrides):
  stats = dict(
    name="Dummy", character_class="Test",
    health=100, attack=0, defense=0, speed=5
  )
  stats.update(overrides)
  return Character(**stats)


def make_buff(stat, magnitude, schools=None, name="Buff", duration=2):
  return StatusEffect(
    name, EffectType.BUFF, EffectCategory.MAGICAL,
    magnitude, duration, schools, stat
  )


def make_debuff(stat, magnitude, schools=None, name="Debuff", duration=2):
  return StatusEffect(
    name, EffectType.DEBUFF, EffectCategory.MAGICAL,
    magnitude, duration, schools, stat
  )


def make_immunity(schools, duration=1):
  return StatusEffect(
    "Immunity", EffectType.IMMUNITY, EffectCategory.MAGICAL,
    0, duration, schools
  )


class TestTakeDamage(unittest.TestCase):

  def test_defense_reduces_damage_without_a_school(self):
    target = make_character(defense=3)

    self.assertEqual(target.take_damage(10), 7)
    self.assertEqual(target.health, 93)

  def test_damage_never_goes_below_zero(self):
    target = make_character(defense=50)

    self.assertEqual(target.take_damage(10), 0)
    self.assertEqual(target.health, 100)

  def test_health_never_goes_below_zero(self):
    target = make_character(health=10)

    target.take_damage(500)

    self.assertEqual(target.health, 0)
    self.assertFalse(target.is_alive())

  def test_resistance_is_a_percentage_reduction(self):
    target = make_character(resistances={SpellSchool.FIRE: 25})

    self.assertEqual(target.take_damage(20, SpellSchool.FIRE), 15)

  def test_negative_resistance_increases_damage(self):
    target = make_character(resistances={SpellSchool.FROST: -10})

    self.assertEqual(target.take_damage(20, SpellSchool.FROST), 22)

  def test_resistance_only_applies_to_its_school(self):
    target = make_character(resistances={SpellSchool.FIRE: 50})

    self.assertEqual(target.take_damage(20, SpellSchool.FROST), 20)

  def test_resistance_is_applied_before_flat_defense(self):
    target = make_character(defense=2, resistances={SpellSchool.FIRE: 25})

    # 20 * 0.75 = 15, then -2 defense
    self.assertEqual(target.take_damage(20, SpellSchool.FIRE), 13)

  def test_immunity_blocks_matching_school_only(self):
    target = make_character()
    target.add_effect(make_immunity([SpellSchool.PHYSICAL]))

    self.assertEqual(target.take_damage(30, SpellSchool.PHYSICAL), 0)
    self.assertEqual(target.take_damage(30, SpellSchool.FIRE), 30)

  def test_expired_immunity_no_longer_protects(self):
    target = make_character()
    target.add_effect(make_immunity([SpellSchool.PHYSICAL], duration=1))

    target.update_effects()

    self.assertFalse(target.is_immune_to(SpellSchool.PHYSICAL))
    self.assertEqual(target.take_damage(30, SpellSchool.PHYSICAL), 30)


class TestStatModifiers(unittest.TestCase):

  def test_buff_raises_and_debuff_lowers_a_stat(self):
    character = make_character(attack=10, defense=5)
    character.add_effect(make_buff(Stat.ATTACK, 10, name="Rage"))
    character.add_effect(make_debuff(Stat.DEFENSE, 3, name="Break"))

    self.assertEqual(character.get_stat(Stat.ATTACK), 20)
    self.assertEqual(character.get_stat(Stat.DEFENSE), 2)
    self.assertEqual(character.get_stat(Stat.SPEED), 5)

  def test_modified_defense_changes_damage_taken(self):
    character = make_character(defense=2)
    character.add_effect(make_buff(Stat.DEFENSE, 7))

    self.assertEqual(character.take_damage(10), 1)

  def test_resistance_buff_applies_only_to_listed_schools(self):
    character = make_character(resistances={SpellSchool.ARCANE: 15})
    character.add_effect(
      make_buff(Stat.RESISTANCE, 15, [SpellSchool.ARCANE, SpellSchool.FIRE])
    )

    self.assertEqual(character.get_resistance(SpellSchool.ARCANE), 30)
    self.assertEqual(character.get_resistance(SpellSchool.FIRE), 15)
    self.assertEqual(character.get_resistance(SpellSchool.FROST), 0)

  def test_resistance_debuff_makes_character_vulnerable(self):
    character = make_character()
    character.add_effect(
      make_debuff(Stat.RESISTANCE, 25, [SpellSchool.ARCANE])
    )

    self.assertEqual(character.get_resistance(SpellSchool.ARCANE), -25)
    self.assertEqual(character.take_damage(20, SpellSchool.ARCANE), 25)

  def test_expired_effects_stop_modifying_stats(self):
    character = make_character(attack=10)
    character.add_effect(make_buff(Stat.ATTACK, 10, duration=1))

    character.update_effects()

    self.assertEqual(character.get_stat(Stat.ATTACK), 10)


class TestEffectsAndHealing(unittest.TestCase):

  def test_reapplying_an_effect_refreshes_instead_of_stacking(self):
    character = make_character(attack=10)

    first = make_buff(Stat.ATTACK, 10, name="Rage", duration=3)
    character.add_effect(first)
    character.update_effects()
    character.add_effect(make_buff(Stat.ATTACK, 10, name="Rage", duration=3))

    self.assertEqual(len(character.active_effects), 1)
    self.assertEqual(character.active_effects[0].remaining_duration, 3)
    self.assertEqual(character.get_stat(Stat.ATTACK), 20)

  def test_different_effects_do_coexist(self):
    character = make_character()
    character.add_effect(make_buff(Stat.ATTACK, 5, name="A"))
    character.add_effect(make_buff(Stat.DEFENSE, 5, name="B"))

    self.assertEqual(len(character.active_effects), 2)

  def test_update_effects_ticks_every_effect_then_drops_expired(self):
    character = make_character()
    short = make_buff(Stat.ATTACK, 1, name="Short", duration=1)
    long = make_buff(Stat.DEFENSE, 1, name="Long", duration=3)
    character.add_effect(short)
    character.add_effect(long)

    character.update_effects()

    self.assertEqual(character.active_effects, [long])
    self.assertEqual(long.remaining_duration, 2)

  def test_heal_restores_health_up_to_max(self):
    character = make_character(health=100)
    character.take_damage(30)

    self.assertEqual(character.heal(20), 20)
    self.assertEqual(character.health, 90)

    self.assertEqual(character.heal(500), 10)
    self.assertEqual(character.health, 100)

  def test_heal_ignores_negative_amounts(self):
    character = make_character()
    character.take_damage(10)

    self.assertEqual(character.heal(-5), 0)
    self.assertEqual(character.health, 90)


if __name__ == "__main__":
  unittest.main()
