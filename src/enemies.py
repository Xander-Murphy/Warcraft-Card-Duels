class Enemy:
  def __init__(self, name, health, attack, defense, speed):
    self.name = name
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