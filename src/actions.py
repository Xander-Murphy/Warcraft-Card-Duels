class Action:
  def __init__(self, actor, ability, targets):
    self.actor = actor
    self.ability = ability
    self.targets = targets

    self.priority = actor.speed + ability.priority

  def execute(self):
    if not self.ability.is_ready():
      return False

    if not self.ability.use():
      return False

    return True