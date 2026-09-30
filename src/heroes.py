class Hero:
  def __init__(
      self,
      name,
      hero_class,
      specialization,
      health,
      attack,
      defense,
      speed
  ):
    self.name = name
    self.hero_class = hero_class
    self.specialization = specialization

    self.max_health = health
    self.health = health

    self.attack = attack
    self.defense = defense
    self.speed = speed

  def is_alive(self):
    return self.health > 0

  def take_damage(self, amount):
    damage = max(0, amount - self.defense)
    self.health = max(0, self.health - damage)
    return damage
