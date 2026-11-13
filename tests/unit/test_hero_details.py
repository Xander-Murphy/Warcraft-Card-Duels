import unittest

from ability_data.hero_abilities import ARCANE_BARRIER, ARCANE_BLAST, SERPENT_STING
from hero_data import BRAEKS, KORYNE
from screens.hero_details import DetailLine, HeroDetails


class TestHeroDetails(unittest.TestCase):

  def setUp(self):
    self.details = HeroDetails()

  def texts(self, hero):
    return [line.text for line in self.details.lines(hero)]

  def test_opens_with_name_role_and_stats(self):
    self.assertEqual(self.details.lines(KORYNE)[:3], [
      DetailLine("Koryne", "heading"),
      DetailLine("Arcane Mage", "description"),
      DetailLine("HP 75   Attack 26   Defense 0   Speed 7", "stats"),
    ])

  def test_only_nonzero_resistances_are_listed(self):
    self.assertIn("Resistances: Arcane +15%", self.texts(KORYNE))
    self.assertFalse(any(text.startswith("Resistances") for text in self.texts(BRAEKS)))

  def test_every_ability_is_listed_with_its_description(self):
    texts = self.texts(BRAEKS)

    for ability in BRAEKS.abilities:
      line = next(text for text in texts if text.startswith(ability.name))
      self.assertEqual(texts[texts.index(line) + 1], ability.description)

  def test_power_is_only_shown_for_abilities_that_deal_damage(self):
    texts = self.texts(KORYNE)

    self.assertIn("Arcane Blast - Single Enemy - Power 30 - Cooldown 2", texts)
    self.assertIn("Arcane Barrier - Self - Cooldown 3", texts)

  def test_heals_show_how_much_they_heal(self):
    from hero_data import LIORA

    self.assertIn("Flash Heal - Single Ally - Heal 30 - Cooldown 1", self.texts(LIORA))


class TestDealsDamage(unittest.TestCase):

  def test_damage_abilities_deal_damage_and_buffs_do_not(self):
    self.assertTrue(ARCANE_BLAST.deals_damage())
    self.assertFalse(ARCANE_BARRIER.deals_damage())

  def test_one_damaging_effect_is_enough(self):
    # Serpent Sting deals damage and also applies poison
    self.assertTrue(SERPENT_STING.deals_damage())


class TestBerserkerRage(unittest.TestCase):

  def test_description_matches_how_long_the_buff_lasts(self):
    # Regression: the description promised "the next three abilities",
    # but the buff has always lasted 3 rounds
    from hero_data import BRAEKS

    rage = next(a for a in BRAEKS.abilities if a.name == "Berserker Rage")
    buff = rage.effects[0].status

    self.assertEqual(buff.duration, 3)
    self.assertIn("3 rounds", rage.description)
    self.assertNotIn("abilities", rage.description)
