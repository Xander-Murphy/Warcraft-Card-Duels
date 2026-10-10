import unittest

from actions import Action
from characters import Character
from enemy_data import DEFIAS_MINER, RAGEFIRE_TROG
from hero_data import BRAEKS, GENJO, KORYNE, SCATTER
from lib.types import TargetType
from targeting import (
  AllAlliesResolver,
  AllEnemiesResolver,
  Battlefield,
  SelfResolver,
  SingleAllyResolver,
  SingleEnemyResolver,
  TargetResolver,
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

  def test_sides_flip_for_an_enemy_actor(self):
    heroes, enemies, battlefield = make_battle()

    self.assertIs(battlefield.allies_of(enemies[1]), enemies)
    self.assertIs(battlefield.enemies_of(enemies[1]), heroes)

  def test_actor_outside_the_battle_is_rejected(self):
    _, _, battlefield = make_battle()
    stranger = Character("Stranger", "Test", 10, 1, 1, 1)

    with self.assertRaises(ValueError):
      battlefield.allies_of(stranger)


class TestResolverCandidates(unittest.TestCase):

  def setUp(self):
    self.heroes, self.enemies, self.battlefield = make_battle()
    self.actor = self.heroes[0]

  def test_self_targets_only_the_actor(self):
    targets = SelfResolver().resolve(self.actor, self.battlefield)

    self.assertEqual(targets, [self.actor])

  def test_single_enemy_candidates_are_the_enemies(self):
    candidates = SingleEnemyResolver().candidates(self.actor, self.battlefield)

    self.assertEqual(candidates, self.enemies)

  def test_all_enemies_hits_every_enemy(self):
    targets = AllEnemiesResolver().resolve(self.actor, self.battlefield)

    self.assertEqual(targets, self.enemies)

  def test_single_ally_candidates_include_the_actor(self):
    candidates = SingleAllyResolver().candidates(self.actor, self.battlefield)

    self.assertEqual(candidates, self.heroes)

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

  def test_enemy_actor_targets_the_heroes(self):
    monster = self.enemies[0]

    targets = AllEnemiesResolver().resolve(monster, self.battlefield)
    single = SingleEnemyResolver().candidates(monster, self.battlefield)

    self.assertEqual(targets, self.heroes)
    self.assertEqual(single, self.heroes)

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

  def test_choice_is_ignored_for_automatic_resolvers(self):
    targets = AllEnemiesResolver().resolve(self.actor, self.battlefield, 2)

    self.assertEqual(targets, self.enemies)

  def test_single_ally_can_pick_another_hero(self):
    result = SingleAllyResolver().resolve(self.actor, self.battlefield, 2)

    self.assertEqual(result, [self.heroes[2]])


class TestResolverRegistry(unittest.TestCase):

  def test_every_target_type_has_a_resolver(self):
    # Guards the future: adding a TargetType without a resolver fails here.
    for target_type in TargetType:
      with self.subTest(target_type=target_type):
        self.assertIsInstance(resolver_for(target_type), TargetResolver)

  def test_each_target_type_maps_to_the_expected_resolver(self):
    expected = {
      TargetType.SELF: SelfResolver,
      TargetType.SINGLE_ALLY: SingleAllyResolver,
      TargetType.ALL_ALLIES: AllAlliesResolver,
      TargetType.SINGLE_ENEMY: SingleEnemyResolver,
      TargetType.ALL_ENEMIES: AllEnemiesResolver,
    }

    for target_type, resolver_class in expected.items():
      with self.subTest(target_type=target_type):
        self.assertIs(type(resolver_for(target_type)), resolver_class)

  def test_abstract_resolver_cannot_be_instantiated(self):
    with self.assertRaises(TypeError):
      TargetResolver()  # pyright: ignore[reportAbstractUsage]

  def test_new_targeting_rule_needs_only_a_subclass(self):
    # Open/Closed: "lowest health enemy" without touching existing code.
    class WeakestEnemyResolver(TargetResolver):
      def candidates(self, actor, battlefield):
        living = [e for e in battlefield.enemies_of(actor) if e.is_alive()]
        return [min(living, key=lambda e: e.health)] if living else []

    heroes, enemies, battlefield = make_battle()
    enemies[2].take_damage(30)

    result = WeakestEnemyResolver().resolve(heroes[0], battlefield)

    self.assertEqual(result, [enemies[2]])


class TestResolversWithRealAbilities(unittest.TestCase):
  """Resolvers driven by the target types declared in the ability data."""

  def test_multi_shot_hits_all_enemies(self):
    # Regression: Multi-Shot used to be declared ALL_ALLIES.
    scatter = SCATTER.clone()
    multi_shot = scatter.abilities[1]

    self.assertEqual(multi_shot.target_type, TargetType.ALL_ENEMIES)

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

  def test_arcane_barrier_resolves_to_the_caster(self):
    heroes, _, battlefield = make_battle()
    koryne = heroes[0]
    barrier = koryne.abilities[2]

    targets = resolver_for(barrier.target_type).resolve(koryne, battlefield)

    self.assertEqual(targets, [koryne])

  def test_enemy_ability_resolves_against_the_party(self):
    heroes, enemies, battlefield = make_battle()
    trog = enemies[0]
    smash = trog.abilities[0]

    candidates = resolver_for(smash.target_type).candidates(trog, battlefield)

    self.assertEqual(candidates, heroes)


if __name__ == "__main__":
  unittest.main()
