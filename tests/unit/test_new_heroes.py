import unittest

from characters import Character
from hero_data import LIORA, TAMARU, TORVALD, VESK
from lib.types import SpellSchool, Stat, TargetType


def dummy(defense=0, health=1_000):
  return Character("Dummy", "Test", health, 0, defense, 1)


def cast(caster, ability_name, targets):
  ability = next(a for a in caster.abilities if a.name == ability_name)
  return ability.apply(caster, targets)


def tick(character, rounds):
  """Run round-end upkeep and return the damage-over-time dealt."""
  return sum(
    result.amount for _ in range(rounds) for result in character.end_round()
  )


class TestNewHeroes(unittest.TestCase):

  def test_class_specialization_and_stats(self):
    # (hero, class, spec, health, attack, defense, speed)
    expected = [
      (LIORA, "Priest", "Holy", 80, 18, 0, 6),
      (TORVALD, "Paladin", "Protection", 120, 17, 4, 4),
      (VESK, "Warlock", "Affliction", 78, 24, 0, 6),
      (TAMARU, "Shaman", "Elemental", 88, 22, 1, 6),
    ]

    for hero, hero_class, spec, health, attack, defense, speed in expected:
      with self.subTest(hero=hero.name):
        self.assertEqual(
          (hero.character_class, hero.specialization), (hero_class, spec)
        )
        self.assertEqual(
          (hero.max_health, hero.attack, hero.defense, hero.speed),
          (health, attack, defense, speed),
        )

  def test_abilities(self):
    expected = {
      LIORA: ["Flash Heal", "Prayer of Healing", "Smite"],
      TORVALD: ["Judgment", "Consecration", "Devotion Aura"],
      VESK: ["Shadow Bolt", "Corruption", "Curse of Weakness"],
      TAMARU: ["Chain Lightning", "Flame Shock", "Healing Wave"],
    }

    for hero, names in expected.items():
      with self.subTest(hero=hero.name):
        self.assertEqual([ability.name for ability in hero.abilities], names)


class TestPriest(unittest.TestCase):

  def test_flash_heal_scales_with_attack(self):
    liora, ally = LIORA.clone(), dummy(health=100)
    ally.take_damage(60)

    cast(liora, "Flash Heal", [ally])

    self.assertEqual(ally.health, 40 + round(30 * 1.18))

  def test_prayer_of_healing_targets_the_whole_party(self):
    self.assertIs(LIORA.abilities[1].target_type, TargetType.ALL_ALLIES)


class TestPaladin(unittest.TestCase):

  def test_consecration_hits_then_burns_for_two_rounds(self):
    torvald, enemies = TORVALD.clone(), [dummy(), dummy()]

    cast(torvald, "Consecration", enemies)

    for enemy in enemies:
      with self.subTest():
        self.assertEqual(enemy.max_health - enemy.health, round(8 * 1.17))
        self.assertEqual(tick(enemy, 3), 10)  # 5 + 5, then it has worn off

  def test_devotion_aura_raises_the_whole_partys_defense(self):
    torvald, ally = TORVALD.clone(), dummy(defense=1)
    self.assertIs(TORVALD.abilities[2].target_type, TargetType.ALL_ALLIES)

    cast(torvald, "Devotion Aura", [torvald, ally])

    self.assertEqual(torvald.get_stat(Stat.DEFENSE), 8)
    self.assertEqual(ally.get_stat(Stat.DEFENSE), 5)


class TestWarlock(unittest.TestCase):

  def test_corruption_out_damages_shadow_bolt_over_its_full_duration(self):
    # Rule: Corruption must beat one Shadow Bolt, even against the
    # toughest current enemy (defense 4)
    for defense in (0, 2, 4):
      with self.subTest(defense=defense):
        bolted, corrupted = dummy(defense), dummy(defense)
        cast(VESK.clone(), "Shadow Bolt", [bolted])
        cast(VESK.clone(), "Corruption", [corrupted])

        bolt_damage = bolted.max_health - bolted.health
        self.assertEqual(corrupted.health, corrupted.max_health)  # no hit
        self.assertGreater(tick(corrupted, 5), bolt_damage)

  def test_corruption_lasts_four_rounds(self):
    target = dummy()
    cast(VESK.clone(), "Corruption", [target])

    self.assertEqual(tick(target, 4), 48)
    self.assertEqual(tick(target, 1), 0)

  def test_curse_of_weakness_lowers_attack(self):
    target = Character("Brute", "Test", 100, 15, 0, 1)

    cast(VESK.clone(), "Curse of Weakness", [target])

    self.assertEqual(target.get_stat(Stat.ATTACK), 5)


class TestShaman(unittest.TestCase):

  def test_flame_shock_hits_then_burns_with_fire_for_three_rounds(self):
    target = dummy()

    cast(TAMARU.clone(), "Flame Shock", [target])

    self.assertEqual(target.max_health - target.health, round(14 * 1.22))
    self.assertEqual(tick(target, 4), 18)

  def test_flame_shock_burn_is_reduced_by_fire_resistance(self):
    target = dummy()
    target.resistances[SpellSchool.FIRE] = 50

    cast(TAMARU.clone(), "Flame Shock", [target])

    self.assertEqual(tick(target, 3), 9)  # 3 per round instead of 6
