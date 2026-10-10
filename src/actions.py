class Action:
  def __init__(self, actor, ability, targets):
    self.actor = actor
    self.ability = ability
    self.targets = targets

    self.priority = actor.speed + ability.priority

  def can_execute(self):
    return self.actor.is_alive() and self.ability.is_ready()

  def execute(self):
    """Spend the cooldown and apply the ability.

    Returns the list of EffectResults, or an empty list if the action
    couldn't be performed (dead actor or ability on cooldown).
    """
    if not self.can_execute():
      return []

    self.ability.use()
    return self.ability.apply(self.actor, self.targets)
