from lib.prototype import Prototype
from lib.types import EffectType, Stat

class StatusEffect(Prototype):
  def __init__(
      self,
      name,
      effect_type, # buff or debuff
      category, # Physical, Magical, Curse, Disease, Poison
      magnitude,
      duration=1,
      schools=None,
      stat=None, # which Stat a buff/debuff modifies (None for DoT / immunity)
      damage_school=None # the school a damage-over-time effect deals damage in
  ):
    self.name = name
    self.effect_type = effect_type
    self.category = category
    self.magnitude = magnitude
    self.duration = duration
    self.remaining_duration = duration
    self.schools = schools if schools else []
    self.stat = stat
    self.damage_school = damage_school

  def is_active(self):
    return self.remaining_duration > 0

  def reduce_duration(self):
    if self.remaining_duration > 0:
      self.remaining_duration -= 1

  def damage_per_round(self):
    """Damage this effect deals at the end of a round (0 if it isn't a DoT)."""
    if self.is_active() and self.effect_type == EffectType.DAMAGE_OVER_TIME:
      return self.magnitude

    return 0

  def affects_school(self, school):
    return school in self.schools

  def modifier_for(self, stat, school=None):
    """Signed amount this effect adds to `stat` (0 if it doesn't touch it).

    Resistance modifiers only apply to the schools the effect lists.
    """
    if not self.is_active() or self.stat is not stat:
      return 0

    if stat is Stat.RESISTANCE and not self.affects_school(school):
      return 0

    if self.effect_type == EffectType.BUFF:
      return self.magnitude
    if self.effect_type == EffectType.DEBUFF:
      return -self.magnitude

    return 0
