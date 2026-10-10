from abc import ABC, abstractmethod
from dataclasses import dataclass

from lib.types import Stat


@dataclass(frozen=True)
class EffectResult:
  """What happened when an effect was applied (used for the combat log/UI)."""
  source: object
  target: object
  description: str
  amount: int = 0


class AbilityEffect(ABC):
  """One thing an ability does to a single target.

  An Ability holds a list of these and applies each in order. To add a new
  kind of ability behavior, subclass this -- Ability, Action and the combat
  system don't change (Open/Closed).
  """

  @abstractmethod
  def apply(self, source, target, ability):
    """Apply the effect and return an EffectResult."""


class DamageEffect(AbilityEffect):
  def calculate_damage(self, source, ability):
    # Ability power scaled by the source's attack as a percentage bonus.
    # Kept in one place so balancing only touches this method.
    attack_bonus = 1 + source.get_stat(Stat.ATTACK) / 100
    return round(ability.power * attack_bonus)

  def apply(self, source, target, ability):
    school = ability.school

    if school is not None and target.is_immune_to(school):
      return EffectResult(
        source, target,
        f"{target.name} is immune to {ability.name}"
      )

    dealt = target.take_damage(self.calculate_damage(source, ability), school)

    return EffectResult(
      source, target,
      f"{source.name}'s {ability.name} hits {target.name} for {dealt}",
      dealt
    )


class HealEffect(AbilityEffect):
  def apply(self, source, target, ability):
    restored = target.heal(ability.power)

    return EffectResult(
      source, target,
      f"{source.name}'s {ability.name} heals {target.name} for {restored}",
      restored
    )


class ApplyStatusEffect(AbilityEffect):
  """Gives the target a copy of a StatusEffect prototype."""

  def __init__(self, status):
    self.status = status

  def apply(self, source, target, ability):
    target.add_effect(self.status.clone())

    return EffectResult(
      source, target,
      f"{target.name} is affected by {self.status.name}"
    )
