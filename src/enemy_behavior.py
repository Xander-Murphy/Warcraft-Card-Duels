import random
from abc import ABC, abstractmethod

from actions import Action
from lib.types import Stat
from targeting import resolver_for


class EnemyBehavior(ABC):
  """Decides what an enemy does on its turn (Strategy pattern).

  Each Enemy holds one of these. A new kind of enemy brain is a new subclass;
  Enemy and Combat don't change (Open/Closed).

  `rng` is an optional random.Random, so tests can make choices repeatable.
  By default the shared `random` module is used.
  """

  name = "Unknown"

  def __init__(self, rng=None):
    self.rng = rng

  def _random(self):
    return self.rng if self.rng is not None else random

  @abstractmethod
  def choose_action(self, enemy, battlefield) -> Action | None:
    """The Action `enemy` wants to take, or None if it has no valid move."""


class RandomBehavior(EnemyBehavior):
  """Uses a random usable ability on a random valid target.

  The basic attack, which is always available, counts as one more option
  alongside the enemy's ready abilities, so each is equally likely.
  """

  name = "Random"

  def choose_action(self, enemy, battlefield) -> Action | None:
    ability = self._choose_ability(enemy)
    targets = self._choose_targets(enemy, ability, battlefield)

    if not targets:
      return None

    return Action(enemy, ability, targets)

  def _choose_ability(self, enemy):
    return self._random().choice(enemy.usable_abilities())

  def _choose_targets(self, enemy, ability, battlefield):
    resolver = resolver_for(ability.target_type)
    candidates = resolver.candidates(enemy, battlefield)

    if not candidates:
      return []

    choice = 0
    if resolver.requires_choice:
      choice = self._random().randrange(len(candidates))

    return resolver.resolve(enemy, battlefield, choice)


class RuleBehavior(EnemyBehavior):
  """A behavior that follows its own targeting rule most of the time.

  With probability `discipline` it uses its strongest ready ability on the
  target its rule picks; otherwise it acts like RandomBehavior. Subclasses
  only say which target they prefer (Template Method), so a new rule is one
  small class.
  """

  DISCIPLINE = 0.75

  def __init__(self, rng=None, discipline=DISCIPLINE):
    super().__init__(rng)
    self.discipline = discipline
    self.fallback = RandomBehavior(rng)

  def choose_action(self, enemy, battlefield) -> Action | None:
    if self._random().random() >= self.discipline:
      return self.fallback.choose_action(enemy, battlefield)

    ability = self.strongest_ability(enemy)
    resolver = resolver_for(ability.target_type)
    candidates = resolver.candidates(enemy, battlefield)

    if not candidates:
      return None

    if resolver.requires_choice:
      targets = [self.pick_target(enemy, candidates)]
    else:
      targets = candidates

    return Action(enemy, ability, targets)

  def strongest_ability(self, enemy):
    """The ready ability (basic attack included) with the most power.

    Ties are broken at random.
    """
    usable = enemy.usable_abilities()
    best = max(ability.power for ability in usable)
    return self._random().choice(
      [ability for ability in usable if ability.power == best]
    )

  @abstractmethod
  def pick_target(self, enemy, candidates):
    """The candidate this behavior wants to hit (candidates are all alive)."""

  def _lowest(self, candidates, key):
    """The candidate with the smallest `key`; ties are broken at random."""
    lowest = min(key(candidate) for candidate in candidates)
    return self._random().choice(
      [candidate for candidate in candidates if key(candidate) == lowest]
    )


class AggressiveBehavior(RuleBehavior):
  """Goes after the target with the least health left, to finish it off."""

  name = "Aggressive"

  def pick_target(self, enemy, candidates):
    return self._lowest(candidates, lambda character: character.health)


class BullyBehavior(RuleBehavior):
  """Goes after the target with the lowest defense (buffs and debuffs count)."""

  name = "Bully"

  def pick_target(self, enemy, candidates):
    return self._lowest(
      candidates, lambda character: character.get_stat(Stat.DEFENSE)
    )


class FocusedBehavior(RuleBehavior):
  """Picks one target and keeps hitting it until it dies, then picks another."""

  name = "Focused"

  def __init__(self, rng=None, discipline=RuleBehavior.DISCIPLINE):
    super().__init__(rng, discipline)
    self.focus = None

  def pick_target(self, enemy, candidates):
    if self.focus not in candidates:
      self.focus = self._random().choice(candidates)

    return self.focus


# Every behavior an enemy can roll when it spawns, each equally likely
BEHAVIORS: tuple[type[EnemyBehavior], ...] = (
  RandomBehavior, AggressiveBehavior, FocusedBehavior, BullyBehavior
)


def roll_behavior(rng=None) -> EnemyBehavior:
  """A new behavior picked at random from BEHAVIORS."""
  behavior_type = (rng if rng is not None else random).choice(BEHAVIORS)
  return behavior_type()
