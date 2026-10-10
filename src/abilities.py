from lib.prototype import Prototype


class Ability(Prototype):
  def __init__(
      self,
      name,
      description,
      power, 
      cooldown,
      target_type,
      school=None,
      priority = 0,
      effects=None,
  ):
    self.name = name
    self.description = description
    self.power = power

    self.cooldown = cooldown
    self.current_cooldown = 0

    self.target_type = target_type
    self.school = school
    self.priority = priority

    # What the ability does, as a list of AbilityEffect objects (composition)
    self.effects = effects if effects else []

  def is_ready(self):
    return self.current_cooldown == 0

  def use(self):
    if not self.is_ready():
      return False
    
    self.current_cooldown = self.cooldown
    return True

  def apply(self, source, targets):
    """Run every effect on every living target; return the EffectResults."""
    results = []

    for target in targets:
      for effect in self.effects:
        if not target.is_alive():
          break

        results.append(effect.apply(source, target, self))

    return results

  def reduce_cooldown(self):
    if self.current_cooldown > 0:
      self.current_cooldown -= 1
