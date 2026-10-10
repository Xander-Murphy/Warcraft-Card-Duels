from ability_data.enemy_abilities import BASIC_ATTACK
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

    # How this enemy chooses what to do (Strategy), and what it falls back
    # on when none of its abilities are ready.
    self.behavior: EnemyBehavior = (
      behavior if behavior is not None else RandomBehavior()
    )
    self.basic_attack = (
      basic_attack if basic_attack is not None else BASIC_ATTACK.clone()
    )

  def has_ability(self, ability):
    return super().has_ability(ability) or ability is self.basic_attack
