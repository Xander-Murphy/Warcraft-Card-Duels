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

  # What this effect does to its target (used to describe abilities)
  deals_damage = False
  heals = False

  @staticmethod
  def scaled_power(source, ability):
    """Ability power scaled by the source's attack as a percentage bonus.

    Damage and healing both use this, so balancing touches one place.
    """
    attack_bonus = 1 + source.get_stat(Stat.ATTACK) / 100
    return round(ability.power * attack_bonus)

  @abstractmethod
  def apply(self, source, target, ability) -> EffectResult:
    """Apply the effect and return an EffectResult."""


class DamageEffect(AbilityEffect):
  deals_damage = True

  def calculate_damage(self, source, ability):
    return self.scaled_power(source, ability)

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
  """Restores health, scaled by the healer's attack like damage is.

  Healing never goes past max health, and targeting only offers living
  allies, so a defeated hero cannot be healed back.
  """

  heals = True

  def apply(self, source, target, ability):
    restored = target.heal(self.scaled_power(source, ability))

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


class DispelEffect(AbilityEffect):
  """Removes the target's harmful effects of the given categories.

  Helpful effects are never touched, so a dispel can't strip a buff.
  """

  def __init__(self, categories):
    self.categories = frozenset(categories)

  def apply(self, source, target, ability):
    removed = target.remove_harmful_effects(self.categories)

    if not removed:
      return EffectResult(source, target, f"{target.name} had nothing to remove")

    names = ", ".join(effect.name for effect in removed)
    return EffectResult(source, target, f"{target.name} is cleansed of {names}")
