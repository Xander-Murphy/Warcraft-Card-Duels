import unittest

from characters import Character
from combat import Combat
from hero_data import BRAEKS, GENJO, KORYNE, SCATTER
from lib.types import Stat


def dummy(defense=0, speed=1):
  return Character("Dummy", "Test", 1_000, 0, defense, speed)


def ability_of(hero, name):
  return next(ability for ability in hero.abilities if ability.name == name)


def damage_from(hero, name, target):
  before = target.health
  ability_of(hero, name).apply(hero, [target])
  return before - target.health


class TestFourthAbilities(unittest.TestCase):

  def test_each_original_hero_gained_a_fourth_ability(self):
    expected = {
      KORYNE: "Arcane Missiles",
      GENJO: "Rupture",
      SCATTER: "Aimed Shot",
      BRAEKS: "Sunder Armor",
    }

    for hero, name in expected.items():
      with self.subTest(hero=hero.name):
        self.assertEqual(hero.abilities[3].name, name)

  def test_arcane_missiles_makes_the_next_arcane_blast_hit_harder(self):
    koryne = KORYNE.clone()
    plain, marked = dummy(), dummy()

    damage_from(koryne, "Arcane Missiles", marked)

    self.assertGreater(
      damage_from(koryne, "Arcane Blast", marked),
      damage_from(koryne, "Arcane Blast", plain),
    )

  def test_rupture_hits_then_bleeds_for_three_rounds(self):
    target = dummy()

    hit = damage_from(GENJO.clone(), "Rupture", target)
    bleed = sum(r.amount for _ in range(4) for r in target.end_round())

    self.assertEqual(hit, round(10 * 1.23))
    self.assertEqual(bleed, 21)

  def test_aimed_shot_is_scatters_hardest_single_hit(self):
    scatter = SCATTER.clone()
    single_hits = [
      ability.power for ability in scatter.abilities if ability.deals_damage()
    ]

    self.assertEqual(max(single_hits), ability_of(scatter, "Aimed Shot").power)

  def test_sunder_armor_lowers_defense_for_two_rounds(self):
    target = dummy(defense=6)

    damage_from(BRAEKS.clone(), "Sunder Armor", target)
    self.assertEqual(target.get_stat(Stat.DEFENSE), 1)

    target.end_round()
    target.end_round()
    self.assertEqual(target.get_stat(Stat.DEFENSE), 6)


class TestNoLookAlikes(unittest.TestCase):

  def signature(self, ability):
    return (
      ability.power, ability.cooldown, ability.target_type, ability.school,
      ability.priority,
      tuple(
        (type(effect).__name__, getattr(getattr(effect, "status", None), "name", None))
        for effect in ability.effects
      ),
    )

  def test_no_two_hero_abilities_are_identical(self):
    from game import Game

    seen = {}
    for hero in Game(None).available_heroes:
      for ability in hero.abilities:
        with self.subTest(ability=ability.name):
          self.assertNotIn(
            self.signature(ability), seen,
            f"{ability.name} is identical to {seen.get(self.signature(ability))}",
          )
        seen[self.signature(ability)] = ability.name

  def test_backstab_lets_genjo_strike_before_a_faster_enemy(self):
    genjo = GENJO.clone()
    quick = dummy(speed=12)
    combat = Combat([genjo], [quick])

    combat.queue_action(genjo, ability_of(genjo, "Backstab"), [quick])
    combat.queue_action(quick, quick.basic_attack, [genjo])
    first = combat.resolve_round()[0]

    self.assertIs(first.source, genjo)

  def test_whirlwind_is_heavier_and_slower_than_multi_shot(self):
    whirlwind = ability_of(BRAEKS, "Whirlwind")
    multi_shot = ability_of(SCATTER, "Multi-Shot")

    self.assertGreater(whirlwind.power, multi_shot.power)
    self.assertGreater(whirlwind.cooldown, multi_shot.cooldown)
