from lib.types import EffectType, SpellSchool, EffectCategory

class StatusEffect:
  def __init__(
      self,
      name,
      effect_type, # buff or debuff
      category, # Physical, Magical, Curse, Disease, Poison
      magnitude,
      duration=1,
      schools=None
  ):
    self.name = name
    self.effect_type = effect_type
    self.category = category
    self.magnitude = magnitude
    self.duration = duration
    self.remaining_duration = duration
    self.schools = schools if schools else []

  def is_active(self):
    return self.remaining_duration > 0

  def reduce_duration(self):
    if self.remaining_duration > 0:
      self.remaining_duration -= 1

  def affects_school(self, school):
    return school in self.schools