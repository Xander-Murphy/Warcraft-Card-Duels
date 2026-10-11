import unittest

from actions import Action
from hero_data import KORYNE, GENJO, SCATTER
from enemy_data import RAGEFIRE_TROG
from ability_data.hero_abilities import ARCANE_BLAST, CLOAK_OF_SHADOWS
from lib.types import SpellSchool


class TestActions(unittest.TestCase):

  def test_action_priority(self):
    normal_action = Action(
      KORYNE,
      ARCANE_BLAST,
      [RAGEFIRE_TROG]
    )

    priority_action = Action(
      GENJO,
      CLOAK_OF_SHADOWS,
      [GENJO]
    )

    self.assertEqual(normal_action.priority, 7)
    self.assertEqual(priority_action.priority, 19)


class TestActionExecution(unittest.TestCase):
  """Runs real abilities from the data modules through Action.execute()."""

  def test_execute_puts_the_ability_on_cooldown(self):
    koryne = KORYNE.clone()
    blast = koryne.abilities[0]

    Action(koryne, blast, [RAGEFIRE_TROG.clone()]).execute()

    self.assertFalse(blast.is_ready())

  def test_ability_on_cooldown_cannot_be_executed(self):
    koryne = KORYNE.clone()
    trog = RAGEFIRE_TROG.clone()
    action = Action(koryne, koryne.abilities[0], [trog])

    action.execute()
    health_after_first_use = trog.health

    self.assertFalse(action.can_execute())
    self.assertEqual(action.execute(), [])
    self.assertEqual(trog.health, health_after_first_use)

  def test_dead_actor_cannot_act(self):
    koryne = KORYNE.clone()
    trog = RAGEFIRE_TROG.clone()
    koryne.take_damage(1000)
    action = Action(koryne, koryne.abilities[0], [trog])

    self.assertFalse(action.can_execute())
    self.assertEqual(action.execute(), [])
    self.assertEqual(trog.health, trog.max_health)

  def test_ability_that_damages_and_applies_a_status(self):
    scatter = SCATTER.clone()
    trog = RAGEFIRE_TROG.clone()
    sting = scatter.abilities[0]  # Serpent Sting: 20 power, attack 21 -> 24

    Action(scatter, sting, [trog]).execute()

    self.assertEqual(trog.health, 16)
    self.assertEqual([e.name for e in trog.active_effects], ["Poison"])

  def test_evasion_blocks_physical_damage_until_it_expires(self):
    genjo = GENJO.clone()
    trog = RAGEFIRE_TROG.clone()
    evasion = genjo.abilities[1]
    smash = trog.abilities[0]

    Action(genjo, evasion, [genjo]).execute()
    blocked = Action(trog, smash, [genjo]).execute()

    self.assertEqual(genjo.health, genjo.max_health)
    self.assertEqual(blocked[0].amount, 0)

    genjo.update_effects()  # end of round: evasion lasts one turn
    smash.reduce_cooldown()
    Action(trog, smash, [genjo]).execute()

    self.assertLess(genjo.health, genjo.max_health)

  def test_cloak_of_shadows_blocks_magic_but_not_physical(self):
    genjo = GENJO.clone()
    Action(genjo, genjo.abilities[2], [genjo]).execute()

    self.assertEqual(genjo.take_damage(30, SpellSchool.ARCANE), 0)
    self.assertGreater(genjo.take_damage(30, SpellSchool.PHYSICAL), 0)

  def test_arcane_barrier_raises_resistance_to_all_schools(self):
    koryne = KORYNE.clone()

    Action(koryne, koryne.abilities[2], [koryne]).execute()

    self.assertEqual(koryne.get_resistance(SpellSchool.ARCANE), 30)
    self.assertEqual(koryne.get_resistance(SpellSchool.PHYSICAL), 15)


class TestActionTargets(unittest.TestCase):

  def test_action_with_only_dead_targets_cannot_execute(self):
    koryne = KORYNE.clone()
    trog = RAGEFIRE_TROG.clone()
    trog.take_damage(10_000)
    action = Action(koryne, koryne.abilities[0], [trog])

    self.assertFalse(action.has_living_target())
    self.assertFalse(action.can_execute())
    self.assertEqual(action.execute(), [])

  def test_fizzled_action_does_not_spend_the_cooldown(self):
    koryne = KORYNE.clone()
    trog = RAGEFIRE_TROG.clone()
    trog.take_damage(10_000)

    Action(koryne, koryne.abilities[0], [trog]).execute()

    self.assertTrue(koryne.abilities[0].is_ready())


if __name__ == "__main__":
  unittest.main()