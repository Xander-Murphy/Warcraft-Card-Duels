from characters import Character
from enemy_behavior import EnemyBehavior, RandomBehavior

class Enemy(Character):
  def __init__(
      self, 
      name, 
      character_class,
      health, 
      attack, 
      defense, 
      speed,
      resistances = None,
      abilities = None,
      behavior = None,
      basic_attack = None
    ):
    super().__init__(
      name,
      character_class,
      health,
      attack,
      defense,
      speed,
      resistances,
      abilities
    )

    # How this enemy chooses what to do (Strategy)
    self.behavior: EnemyBehavior = (
      behavior if behavior is not None else RandomBehavior()
    )

    # A custom basic attack (for bosses, say) replaces the default one
    if basic_attack is not None:
      self.basic_attack = basic_attack
