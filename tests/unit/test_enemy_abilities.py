import unittest

from characters import Character
from effects_data import AGONY, BURN, CHILLED, HAMSTRUNG, WEAKENED
from encounters import (
  DEADMINES_ENCOUNTERS, RAGEFIRE_ENCOUNTERS, WAILING_CAVERNS_ENCOUNTERS
)
from enemy_data import DEVIATE_VIPER, DEFIAS_SQUALLSHAPER, MOLTEN_ELEMENTAL
from lib.types import EffectCategory, SpellSchool, Stat, TargetType
from ability_effects import ApplyStatusEffect

DUNGEONS = {
  "Ragefire Chasm": RAGEFIRE_ENCOUNTERS,
  "Wailing Caverns": WAILING_CAVERNS_ENCOUNTERS,
  "The Deadmines": DEADMINES_ENCOUNTERS,
}


def regular_enemies():
  """Every enemy that can spawn in an encounter (bosses come later)."""
  seen = {}
  for encounters in DUNGEONS.values():
    for pool in encounters.values():
      for enemy in pool:
        seen[enemy.name] = enemy
  return list(seen.values())


def applies_a_status(ability):
  return any(isinstance(effect, ApplyStatusEffect) for effect in ability.effects)


def cast_damage(enemy, ability, party_size=3):
  """Total damage one cast can do: the hit scaled by attack, plus the whole
  damage-over-time, times the party size for abilities that hit everyone."""
  total = 0
  if ability.deals_damage():
    total += ability.power * (1 + enemy.attack / 100)
  for effect in ability.effects:
    if isinstance(effect, ApplyStatusEffect):
      total += effect.status.damage_per_round() * effect.status.duration
  if ability.target_type is TargetType.ALL_ENEMIES:
    total *= party_size
  return total


def average_best_cast(pool):
  return sum(
    max(cast_damage(enemy, a) for a in enemy.abilities + [enemy.basic_attack])
    for enemy in pool
  ) / len(pool)


def dummy():
  return Character("Dummy", "Test", 1_000, 10, 0, 6)


def tick(character, rounds):
  return sum(r.amount for _ in range(rounds) for r in character.end_round())


class TestEnemyKits(unittest.TestCase):

  def test_every_regular_enemy_has_two_abilities(self):
    enemies = regular_enemies()
    self.assertEqual(len(enemies), 24)

    for enemy in enemies:
      with self.subTest(enemy=enemy.name):
        self.assertEqual(len(enemy.abilities), 2)

  def test_physical_enemies_only_use_physical_abilities(self):
    for enemy in regular_enemies():
      if enemy.character_class != "Physical":
        continue
      for ability in enemy.abilities:
        with self.subTest(enemy=enemy.name, ability=ability.name):
          self.assertIs(ability.school, SpellSchool.PHYSICAL)

  def test_casters_use_magic_and_at_least_one_effect(self):
    for enemy in regular_enemies():
      if enemy.character_class != "Caster":
        continue
      with self.subTest(enemy=enemy.name):
        for ability in enemy.abilities:
          self.assertIsNot(ability.school, SpellSchool.PHYSICAL)
        self.assertTrue(any(applies_a_status(a) for a in enemy.abilities))

  def test_molten_elemental_is_now_a_caster(self):
    self.assertEqual(MOLTEN_ELEMENTAL.character_class, "Caster")

  def test_the_final_encounter_hits_harder_than_the_first(self):
    for dungeon, encounters in DUNGEONS.items():
      with self.subTest(dungeon=dungeon):
        self.assertGreater(
          average_best_cast(encounters[3]), average_best_cast(encounters[1])
        )

  def test_enemy_health_rises_with_every_encounter(self):
    for dungeon, encounters in DUNGEONS.items():
      with self.subTest(dungeon=dungeon):
        health = [
          sum(e.max_health for e in encounters[n]) / len(encounters[n])
          for n in (1, 2, 3)
        ]
        self.assertEqual(health, sorted(health))


class TestNewEffects(unittest.TestCase):

  def apply(self, status):
    target = dummy()
    target.add_effect(status.clone())
    return target

  def test_burn_is_fire_damage_over_three_rounds(self):
    self.assertEqual(tick(self.apply(BURN), 4), 12)
    self.assertIs(BURN.damage_school, SpellSchool.FIRE)

  def test_agony_is_a_shadow_curse_over_four_rounds(self):
    self.assertEqual(tick(self.apply(AGONY), 5), 20)
    self.assertIs(AGONY.category, EffectCategory.CURSE)

  def test_slows_lower_speed_and_weakened_lowers_attack(self):
    self.assertEqual(self.apply(CHILLED).get_stat(Stat.SPEED), 3)
    self.assertEqual(self.apply(HAMSTRUNG).get_stat(Stat.SPEED), 3)
    self.assertEqual(self.apply(WEAKENED).get_stat(Stat.ATTACK), 4)

  def test_hamstrung_is_physical_but_the_magic_slows_are_not(self):
    self.assertIs(HAMSTRUNG.category, EffectCategory.PHYSICAL)
    self.assertIs(CHILLED.category, EffectCategory.MAGICAL)


class TestSignatureAbilities(unittest.TestCase):

  def test_poison_bite_poisons(self):
    target = dummy()
    DEVIATE_VIPER.clone().abilities[1].apply(DEVIATE_VIPER.clone(), [target])

    self.assertEqual([e.name for e in target.active_effects], ["Poison"])

  def test_frostbolt_chills(self):
    target = dummy()
    squallshaper = DEFIAS_SQUALLSHAPER.clone()
    squallshaper.abilities[0].apply(squallshaper, [target])

    self.assertEqual(target.get_stat(Stat.SPEED), 3)
