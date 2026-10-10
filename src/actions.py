class Action:
  def __init__(self, actor, ability, targets):
    self.actor = actor
    self.ability = ability
    self.targets = targets

    self.priority = actor.speed + ability.priority

  def has_living_target(self):
    return any(target.is_alive() for target in self.targets)

  def can_execute(self):
    return (
      self.actor.is_alive()
      and self.ability.is_ready()
      and self.has_living_target()
    )

  def execute(self):
    """Spend the cooldown and apply the ability.

    Returns the list of EffectResults, or an empty list if the action
    couldn't be performed (dead actor, ability on cooldown, or every
    target already dead).
    """
    if not self.can_execute():
      return []

    self.ability.use()
    return self.ability.apply(self.actor, self.targets)
