import copy


class Prototype:
  """Mixin for objects that are defined once as data and copied per use.

  hero_data / enemy_data / ability_data hold *prototypes*. They describe a
  character or ability but must never be mutated. Anything that needs to take
  damage, spend a cooldown, or gain a status effect works on a clone, so two
  enemies built from the same prototype never share health or cooldowns.
  """

  def clone(self):
    return copy.deepcopy(self)
