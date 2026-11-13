import unittest

from ability_effects import DispelEffect
import effects_data as fx
from hero_data import GENJO
from lib.types import EffectCategory, SpellSchool


def cloak_of(genjo):
  return next(a for a in genjo.abilities if a.name == "Cloak of Shadows")


def names(character):
  return sorted(effect.name for effect in character.active_effects)


class TestCloakOfShadows(unittest.TestCase):

  def setUp(self):
    self.genjo = GENJO.clone()

  def afflict(self, *statuses):
    for status in statuses:
      self.genjo.add_effect(status.clone())

  def test_removes_magical_effects_curses_and_poison(self):
    self.afflict(fx.FLAME_SHOCK, fx.CORRUPTION, fx.POISON, fx.ARCANE_VULNERABILITY)

    cloak_of(self.genjo).apply(self.genjo, [self.genjo])

    self.assertEqual(names(self.genjo), ["Magical Immunity"])

  def test_leaves_physical_effects_alone(self):
    self.afflict(fx.BLEED, fx.ARMOR_BREAK, fx.POISON)

    cloak_of(self.genjo).apply(self.genjo, [self.genjo])

    self.assertEqual(names(self.genjo), ["Armor Break", "Bleed", "Magical Immunity"])

  def test_never_removes_helpful_effects(self):
    self.afflict(fx.ARCANE_BARRIER)  # a helpful magical buff

    cloak_of(self.genjo).apply(self.genjo, [self.genjo])

    self.assertIn("Arcane Barrier", names(self.genjo))

  def test_still_grants_magical_immunity(self):
    cloak_of(self.genjo).apply(self.genjo, [self.genjo])

    self.assertTrue(self.genjo.is_immune_to(SpellSchool.FIRE))
    self.assertFalse(self.genjo.is_immune_to(SpellSchool.PHYSICAL))


class TestDispelEffect(unittest.TestCase):

  def test_reports_what_it_removed(self):
    genjo = GENJO.clone()
    genjo.add_effect(fx.POISON.clone())
    dispel = DispelEffect([EffectCategory.POISON])

    result = dispel.apply(genjo, genjo, None)

    self.assertEqual(result.description, "Genjo is cleansed of Poison")

  def test_says_so_when_there_is_nothing_to_remove(self):
    genjo = GENJO.clone()
    genjo.add_effect(fx.BLEED.clone())

    result = DispelEffect([EffectCategory.MAGICAL]).apply(genjo, genjo, None)

    self.assertEqual(result.description, "Genjo had nothing to remove")
    self.assertEqual(names(genjo), ["Bleed"])
