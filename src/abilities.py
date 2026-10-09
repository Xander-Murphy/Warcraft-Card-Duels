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
  ):
    self.name = name
    self.description = description
    self.power = power

    self.cooldown = cooldown
    self.current_cooldown = 0

    self.target_type = target_type
    self.school = school
    self.priority = priority

  def is_ready(self):
    return self.current_cooldown == 0

  def use(self):
    if not self.is_ready():
      return False
    
    self.current_cooldown = self.cooldown
    return True



  def reduce_cooldown(self):
    if self.current_cooldown > 0:
      self.current_cooldown -= 1
