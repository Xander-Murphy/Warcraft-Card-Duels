import unittest

from enemy_data import DEVIATE_RAVAGER
from hero_data import KORYNE


class TestCloning(unittest.TestCase):

  def test_clone_is_a_separate_object_with_the_same_stats(self):
    clone = KORYNE.clone()

    self.assertIsNot(clone, KORYNE)
    self.assertEqual(clone.name, KORYNE.name)
    self.assertEqual(clone.health, KORYNE.health)
    self.assertEqual(clone.specialization, KORYNE.specialization)

  # Regression: every enemy of a type used to be the same shared object, so hurting one hurt them all.
  def test_damaging_a_clone_does_not_touch_the_prototype_or_siblings(self):
    first = DEVIATE_RAVAGER.clone()
    second = DEVIATE_RAVAGER.clone()

    first.take_damage(20)

    self.assertLess(first.health, DEVIATE_RAVAGER.max_health)
    self.assertEqual(second.health, DEVIATE_RAVAGER.max_health)
    self.assertEqual(DEVIATE_RAVAGER.health, DEVIATE_RAVAGER.max_health)

  # Regression: cooldowns used to be shared between copies of a character through the shared prototype.
  def test_cloned_abilities_have_independent_cooldowns(self):
    first = KORYNE.clone()
    second = KORYNE.clone()

    first.abilities[0].use()

    self.assertFalse(first.abilities[0].is_ready())
    self.assertTrue(second.abilities[0].is_ready())
    self.assertTrue(KORYNE.abilities[0].is_ready())


if __name__ == "__main__":
  unittest.main()
