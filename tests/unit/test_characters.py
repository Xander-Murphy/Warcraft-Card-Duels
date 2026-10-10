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


class TestRoundEnd(unittest.TestCase):

  def poison(self, duration=3, magnitude=10):
    return StatusEffect(
      "Poison", EffectType.DAMAGE_OVER_TIME, EffectCategory.POISON,
      magnitude, duration, damage_school=SpellSchool.NATURE
    )

  def test_lose_health_ignores_defense_and_resistance(self):
    character = make_character(defense=50, resistances={SpellSchool.FIRE: 90})

    self.assertEqual(character.lose_health(30), 30)
    self.assertEqual(character.health, 70)

  def test_lose_health_cannot_go_below_zero_or_be_negative(self):
    character = make_character(health=10)

    character.lose_health(-5)
    self.assertEqual(character.health, 10)

    character.lose_health(500)
    self.assertEqual(character.health, 0)

  def test_damage_over_time_effect_reports_its_damage_while_active(self):
    effect = self.poison(duration=1)

    self.assertEqual(effect.damage_per_round(), 10)

    effect.reduce_duration()
    self.assertEqual(effect.damage_per_round(), 0)

  def test_non_damage_effects_deal_no_damage_per_round(self):
    self.assertEqual(make_buff(Stat.ATTACK, 10).damage_per_round(), 0)
    self.assertEqual(make_debuff(Stat.DEFENSE, 10).damage_per_round(), 0)
    self.assertEqual(make_immunity([SpellSchool.FIRE]).damage_per_round(), 0)

  def test_end_round_deals_damage_over_time_and_reports_it(self):
    character = make_character(defense=3)
    character.add_effect(self.poison())

    results = character.end_round()

    self.assertEqual(character.health, 93)  # 10 nature damage - 3 defense
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0].amount, 7)
    self.assertIs(results[0].target, character)

  def test_damage_over_time_is_reduced_by_resistance_to_its_school(self):
    character = make_character(resistances={SpellSchool.NATURE: 50})
    character.add_effect(self.poison())

    character.end_round()

    self.assertEqual(character.health, 95)

  def test_other_school_resistance_does_not_reduce_poison(self):
    character = make_character(resistances={SpellSchool.FIRE: 50})
    character.add_effect(self.poison())

    character.end_round()

    self.assertEqual(character.health, 90)

  def test_immunity_to_the_school_blocks_damage_over_time(self):
    character = make_character()
    character.add_effect(self.poison())
    character.add_effect(make_immunity([SpellSchool.NATURE], duration=2))

    results = character.end_round()

    self.assertEqual(character.health, 100)
    self.assertEqual(results[0].amount, 0)
    self.assertIn("immune", results[0].description)

  def test_immunity_to_a_different_school_does_not_block_poison(self):
    character = make_character()
    character.add_effect(self.poison())
    character.add_effect(make_immunity([SpellSchool.PHYSICAL], duration=2))

    character.end_round()

    self.assertEqual(character.health, 90)

  def test_damage_over_time_without_a_school_only_faces_defense(self):
    character = make_character(
      defense=4, resistances={SpellSchool.NATURE: 50}
    )
    character.add_effect(StatusEffect(
      "Curse", EffectType.DAMAGE_OVER_TIME, EffectCategory.CURSE, 10, 2
    ))

    character.end_round()

    self.assertEqual(character.health, 94)

  def test_end_round_expires_effects(self):
    character = make_character()
    character.add_effect(self.poison(duration=1))

    character.end_round()

    self.assertEqual(character.active_effects, [])

  def test_end_round_ticks_ability_cooldowns(self):
    from abilities import Ability
    from lib.types import TargetType
    ability = Ability("A", "", 1, 3, TargetType.SELF)
    character = make_character(abilities=[ability])
    ability.use()

    character.end_round()

    self.assertEqual(ability.current_cooldown, 2)

  def test_end_round_does_not_tick_a_character_killed_by_poison_twice(self):
    character = make_character(health=5)
    character.add_effect(self.poison())
    character.add_effect(StatusEffect(
      "Bleed", EffectType.DAMAGE_OVER_TIME, EffectCategory.PHYSICAL, 10, 3
    ))

    results = character.end_round()

    self.assertEqual(character.health, 0)
    self.assertEqual(len(results), 1)

  def test_end_round_with_nothing_active_reports_nothing(self):
    self.assertEqual(make_character().end_round(), [])


class TestUsableAbilities(unittest.TestCase):

  def make(self, *cooldowns):
    from abilities import Ability
    from lib.types import TargetType
    abilities = [
      Ability(f"A{i}", "", 10, cooldown, TargetType.SINGLE_ENEMY)
      for i, cooldown in enumerate(cooldowns)
    ]
    return make_character(abilities=abilities)

  def test_every_character_has_its_own_basic_attack(self):
    first, second = make_character(), make_character()

    self.assertEqual(first.basic_attack.name, "Basic Attack")
    self.assertEqual(first.basic_attack.power, 15)
    self.assertIsNot(first.basic_attack, second.basic_attack)

  def test_ready_abilities_are_usable_and_the_basic_attack_is_not(self):
    character = self.make(2, 3)

    self.assertEqual(character.usable_abilities(), character.abilities)
    self.assertFalse(character.can_use(character.basic_attack))

  def test_abilities_on_cooldown_are_not_usable(self):
    character = self.make(2, 3)
    character.abilities[0].use()

    self.assertEqual(character.usable_abilities(), [character.abilities[1]])
    self.assertFalse(character.can_use(character.abilities[0]))
    self.assertTrue(character.can_use(character.abilities[1]))

  def test_basic_attack_is_the_fallback_when_nothing_is_ready(self):
    character = self.make(2, 3)
    for ability in character.abilities:
      ability.use()

    self.assertEqual(character.usable_abilities(), [character.basic_attack])
    self.assertTrue(character.can_use(character.basic_attack))
    self.assertFalse(character.can_use(character.abilities[0]))

  def test_character_with_no_abilities_can_always_use_the_basic_attack(self):
    character = make_character()

    self.assertEqual(character.usable_abilities(), [character.basic_attack])

  def test_other_characters_abilities_are_never_usable(self):
    character, other = self.make(2), self.make(2)

    self.assertFalse(character.can_use(other.abilities[0]))
    self.assertFalse(character.can_use(other.basic_attack))


if __name__ == "__main__":
  unittest.main()
