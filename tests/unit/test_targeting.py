import unittest

from actions import Action
from enemy_data import DEFIAS_MINER, RAGEFIRE_TROG
from hero_data import BRAEKS, GENJO, KORYNE
from targeting import (
  AllAlliesResolver,
  AllEnemiesResolver,
  Battlefield,
  SelfResolver,
  SingleAllyResolver,
  SingleEnemyResolver,
  resolver_for,
)


def make_battle():
  heroes = [KORYNE.clone(), GENJO.clone(), BRAEKS.clone()]
  enemies = [RAGEFIRE_TROG.clone(), DEFIAS_MINER.clone(), RAGEFIRE_TROG.clone()]
  return heroes, enemies, Battlefield(heroes, enemies)


def kill(character):
  character.take_damage(10_000)


class TestBattlefield(unittest.TestCase):

  def test_hero_sees_party_as_allies_and_monsters_as_enemies(self):
    heroes, enemies, battlefield = make_battle()

    self.assertIs(battlefield.allies_of(heroes[0]), heroes)
    self.assertIs(battlefield.enemies_of(heroes[0]), enemies)


class TestResolverCandidates(unittest.TestCase):

  def setUp(self):
    self.heroes, self.enemies, self.battlefield = make_battle()
    self.actor = self.heroes[0]

  def test_self_targets_only_the_actor(self):
    targets = SelfResolver().resolve(self.actor, self.battlefield)

    self.assertEqual(targets, [self.actor])

  def test_all_enemies_hits_every_enemy(self):
    targets = AllEnemiesResolver().resolve(self.actor, self.battlefield)

    self.assertEqual(targets, self.enemies)

  def test_all_allies_hits_the_whole_party(self):
    targets = AllAlliesResolver().resolve(self.actor, self.battlefield)

    self.assertEqual(targets, self.heroes)

  def test_dead_characters_are_never_candidates(self):
    kill(self.enemies[1])
    kill(self.heroes[2])

    enemy_candidates = SingleEnemyResolver().candidates(
      self.actor, self.battlefield
    )
    ally_candidates = AllAlliesResolver().candidates(
      self.actor, self.battlefield
    )

    self.assertEqual(enemy_candidates, [self.enemies[0], self.enemies[2]])
    self.assertEqual(ally_candidates, [self.heroes[0], self.heroes[1]])

  def test_dead_actor_cannot_target_self(self):
    kill(self.actor)

    self.assertEqual(SelfResolver().resolve(self.actor, self.battlefield), [])

  def test_enemy_ally_targeting_stays_on_the_monster_side(self):
    monster = self.enemies[0]

    targets = AllAlliesResolver().resolve(monster, self.battlefield)

    self.assertEqual(targets, self.enemies)


class TestResolverChoice(unittest.TestCase):

  def setUp(self):
    self.heroes, self.enemies, self.battlefield = make_battle()
    self.actor = self.heroes[0]

  def test_which_resolvers_need_the_player_to_choose(self):
    self.assertTrue(SingleEnemyResolver().requires_choice)
    self.assertTrue(SingleAllyResolver().requires_choice)
    self.assertFalse(AllEnemiesResolver().requires_choice)
    self.assertFalse(AllAlliesResolver().requires_choice)
    self.assertFalse(SelfResolver().requires_choice)

  def test_single_target_resolves_the_chosen_candidate(self):
    resolver = SingleEnemyResolver()

    for index, enemy in enumerate(self.enemies):
      with self.subTest(choice=index):
        self.assertEqual(
          resolver.resolve(self.actor, self.battlefield, index), [enemy]
        )

  def test_choice_indexes_living_candidates_only(self):
    kill(self.enemies[0])

    result = SingleEnemyResolver().resolve(self.actor, self.battlefield, 0)

    self.assertEqual(result, [self.enemies[1]])

  def test_invalid_choice_resolves_to_nobody(self):
    resolver = SingleEnemyResolver()

    self.assertEqual(resolver.resolve(self.actor, self.battlefield, 99), [])
    self.assertEqual(resolver.resolve(self.actor, self.battlefield, -1), [])

  def test_single_ally_can_pick_another_hero(self):
    result = SingleAllyResolver().resolve(self.actor, self.battlefield, 2)

    self.assertEqual(result, [self.heroes[2]])


class TestResolversWithRealAbilities(unittest.TestCase):
  """Resolvers driven by the target types declared in the ability data."""

  def test_whirlwind_resolves_to_every_living_enemy_and_hits_them(self):
    heroes, enemies, battlefield = make_battle()
    braeks = heroes[2]
    kill(enemies[1])
    whirlwind = braeks.abilities[2]

    targets = resolver_for(whirlwind.target_type).resolve(braeks, battlefield)
    Action(braeks, whirlwind, targets).execute()

    self.assertEqual(targets, [enemies[0], enemies[2]])
    self.assertLess(enemies[0].health, enemies[0].max_health)
    self.assertLess(enemies[2].health, enemies[2].max_health)
    self.assertEqual(enemies[1].health, 0)


if __name__ == "__main__":
  unittest.main()
