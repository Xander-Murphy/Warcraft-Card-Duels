from ability_effects import EffectResult
from lib.prototype import Prototype
from lib.types import SpellSchool, EffectType, Stat

class Character(Prototype):
  def __init__(
      self, 
      name, 
      character_class, 
      health, 
      attack, 
      defense, 
      speed, 
      resistances=None,
      abilities=None
    ):

      self.name = name
      self.character_class = character_class

      self.max_health = health
      self.health = health

      self.attack = attack
      self.defense = defense
      self.speed = speed

      self.resistances = resistances if resistances else {
         SpellSchool.PHYSICAL: 0,
         SpellSchool.ARCANE: 0,
         SpellSchool.FIRE: 0,
         SpellSchool.FROST: 0,
         SpellSchool.HOLY: 0,
         SpellSchool.NATURE: 0,
         SpellSchool.SHADOW: 0,
      }


      self.abilities = abilities if abilities else []
      self.active_effects = []

  def is_alive(self):
     return self.health > 0

  def get_stat(self, stat):
    """Base attack/defense/speed plus any active buffs and debuffs."""
    base = {
      Stat.ATTACK: self.attack,
      Stat.DEFENSE: self.defense,
      Stat.SPEED: self.speed,
    }[stat]

    return base + sum(
      effect.modifier_for(stat) for effect in self.active_effects
    )

  def get_resistance(self, school):
    """Base resistance (a percentage) plus active resistance buffs/debuffs."""
    return self.resistances.get(school, 0) + sum(
      effect.modifier_for(Stat.RESISTANCE, school)
      for effect in self.active_effects
    )

  def is_immune_to(self, school):
    return any(
      effect.effect_type == EffectType.IMMUNITY
      and effect.is_active()
      and effect.affects_school(school)
      for effect in self.active_effects
    )

  def take_damage(self, amount, school=None):
    """Apply incoming damage and return how much health was actually lost.

    Order: immunity -> resistance (percentage) -> defense (flat).
    With no school, only defense applies.
    """
    if school is not None:
      if self.is_immune_to(school):
        return 0

      amount = amount * (1 - self.get_resistance(school) / 100)

    return self.lose_health(
      max(0, round(amount) - self.get_stat(Stat.DEFENSE))
    )

  def lose_health(self, amount):
    """Remove health directly (no defense/resistance) and return the amount."""
    amount = max(0, amount)
    self.health = max(0, self.health - amount)
    return amount

  def heal(self, amount):
    """Restore health (capped at max_health) and return the amount restored."""
    restored = min(max(0, amount), self.max_health - self.health)
    self.health += restored
    return restored

  def add_effect(self, effect):
    # Re-applying an effect refreshes it rather than stacking a duplicate.
    self.active_effects = [
      existing for existing in self.active_effects
      if existing.name != effect.name
    ]
    self.active_effects.append(effect)

  def remove_effect(self, effect):
     if effect in self.active_effects:
        self.active_effects.remove(effect)

  def end_round(self) -> list:
    """Round-end upkeep: damage over time, then effect and cooldown ticks.

    Damage over time goes through take_damage in the effect's school, so
    resistance, immunity and defense apply like any other damage.
    Returns an EffectResult for each damage-over-time tick.
    """
    results = []

    for effect in self.active_effects:
      damage = effect.damage_per_round()

      if damage > 0 and self.is_alive():
        school = effect.damage_school

        if school is not None and self.is_immune_to(school):
          description = f"{self.name} is immune to {effect.name}"
          dealt = 0
        else:
          dealt = self.take_damage(damage, school)
          description = f"{self.name} takes {dealt} damage from {effect.name}"

        results.append(EffectResult(None, self, description, dealt))

    self.update_effects()

    for ability in self.abilities:
      ability.reduce_cooldown()

    return results

  def update_effects(self):
    for effect in self.active_effects:
      effect.reduce_duration()

    self.active_effects = [
      effect for effect in self.active_effects
      if effect.is_active()
    ]
