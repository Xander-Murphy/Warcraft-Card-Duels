class Character:
  def __init__(
      self, 
      name, 
      character_class, 
      health, attack, 
      defense, speed, 
      abilities=None
    ):

      self.name = name
      self.character_class = character_class

      self.max_health = health
      self.health = health

      self.attack = attack
      self.defense = defense
      self.speed = speed

      self.abilities = abilities if abilities else []

  def is_alive(self):
     return self.health > 0

  def take_damage(self, amount):
      damage = max(0, amount - self.defense)
      self.health = max(0, self.health - damage)
      return damage