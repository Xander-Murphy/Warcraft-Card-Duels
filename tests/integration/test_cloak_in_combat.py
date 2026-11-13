import unittest

import effects_data as fx
from characters import Character
from combat import Combat
from hero_data import GENJO


class TestCloakInCombat(unittest.TestCase):

  def test_cloak_stops_poison_and_curses_ticking_that_round(self):
    genjo = GENJO.clone()
    genjo.add_effect(fx.POISON.clone())
    genjo.add_effect(fx.CORRUPTION.clone())
    dummy = Character("Dummy", "Test", 1_000, 0, 0, 1)
    combat = Combat([genjo], [dummy])
    cloak = next(a for a in genjo.abilities if a.name == "Cloak of Shadows")

    combat.queue_action(genjo, cloak, [genjo])
    combat.queue_action(dummy, dummy.basic_attack, [genjo])
    log = [result.description for result in combat.resolve_round()]

    self.assertIn("Genjo is cleansed of Poison, Corruption", log)
    self.assertFalse(any("from Poison" in line or "from Corruption" in line for line in log))
