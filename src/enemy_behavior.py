import random
from abc import ABC, abstractmethod

from actions import Action
from targeting import resolver_for


class EnemyBehavior(ABC):
  """Decides what an enemy does on its turn (Strategy pattern).

  Each Enemy holds one of these. A new kind of enemy brain is a new subclass;
  Enemy and Combat don't change (Open/Closed).
  """

  @abstractmethod
  def choose_action(self, enemy, battlefield) -> Action | None:
    """The Action `enemy` wants to take, or None if it has no valid move."""


class RandomBehavior(EnemyBehavior):
  """Uses a random ready ability on a random valid target.

  If none of the enemy's abilities are ready (or it has none), it uses its
  basic attack instead.

  `rng` is an optional random.Random, so tests can make choices repeatable.
  By default the shared `random` module is used.
  """

  def __init__(self, rng=None):
    self.rng = rng

  def _random(self):
    return self.rng if self.rng is not None else random

  def choose_action(self, enemy, battlefield) -> Action | None:
    ability = self._choose_ability(enemy)
    targets = self._choose_targets(enemy, ability, battlefield)

    if not targets:
      return None

    return Action(enemy, ability, targets)

  def _choose_ability(self, enemy):
    ready = [ability for ability in enemy.abilities if ability.is_ready()]

    if not ready:
      return enemy.basic_attack

    return self._random().choice(ready)

  def _choose_targets(self, enemy, ability, battlefield):
    resolver = resolver_for(ability.target_type)
    candidates = resolver.candidates(enemy, battlefield)

    if not candidates:
      return []

    choice = 0
    if resolver.requires_choice:
      choice = self._random().randrange(len(candidates))

    return resolver.resolve(enemy, battlefield, choice)
