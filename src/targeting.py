from abc import ABC, abstractmethod

from lib.types import TargetType


class Battlefield:
  """The two sides of a fight, seen from any actor's point of view.

  "Ally" and "enemy" are relative: a hero's enemies are the monsters, a
  monster's enemies are the heroes.
  """

  def __init__(self, heroes, enemies):
    self.heroes = heroes
    self.enemies = enemies

  def allies_of(self, actor):
    return self.heroes if self._is_hero(actor) else self.enemies

  def enemies_of(self, actor):
    return self.enemies if self._is_hero(actor) else self.heroes

  def _is_hero(self, actor):
    if any(actor is hero for hero in self.heroes):
      return True

    if any(actor is enemy for enemy in self.enemies):
      return False

    raise ValueError(f"{actor.name} is not part of this battlefield")


def _living(characters):
  return [character for character in characters if character.is_alive()]


class TargetResolver(ABC):
  """Decides who an ability can hit.

  Subclasses only say which characters are valid candidates and whether the
  player must pick one (requires_choice). Everything else is shared, so a new
  targeting rule is one small subclass (Open/Closed).
  """

  requires_choice = False

  @abstractmethod
  def candidates(self, actor, battlefield) -> list:
    """Every living character this ability could target."""

  def resolve(self, actor, battlefield, choice=0) -> list:
    """The characters the ability will actually hit.

    `choice` is an index into candidates(); it's only used when the player
    has to pick a single target. An invalid choice resolves to no targets.
    """
    candidates = self.candidates(actor, battlefield)

    if not self.requires_choice:
      return candidates

    if 0 <= choice < len(candidates):
      return [candidates[choice]]

    return []


class SelfResolver(TargetResolver):
  def candidates(self, actor, battlefield):
    return _living([actor])


class SingleAllyResolver(TargetResolver):
  requires_choice = True

  def candidates(self, actor, battlefield):
    return _living(battlefield.allies_of(actor))


class AllAlliesResolver(TargetResolver):
  def candidates(self, actor, battlefield):
    return _living(battlefield.allies_of(actor))


class SingleEnemyResolver(TargetResolver):
  requires_choice = True

  def candidates(self, actor, battlefield):
    return _living(battlefield.enemies_of(actor))


class AllEnemiesResolver(TargetResolver):
  def candidates(self, actor, battlefield):
    return _living(battlefield.enemies_of(actor))


# Resolvers hold no state, so one shared instance per target type is enough.
_RESOLVERS = {
  TargetType.SELF: SelfResolver(),
  TargetType.SINGLE_ALLY: SingleAllyResolver(),
  TargetType.ALL_ALLIES: AllAlliesResolver(),
  TargetType.SINGLE_ENEMY: SingleEnemyResolver(),
  TargetType.ALL_ENEMIES: AllEnemiesResolver(),
}


def resolver_for(target_type):
  return _RESOLVERS[target_type]
