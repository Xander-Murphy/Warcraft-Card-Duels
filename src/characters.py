from lib.types import SpellSchool

class Character:
  def __init__(
      self, 
      name, 
      character_class, 
      health, 
      attack, 
      defense, 
      speed, 
      resistances=None,
      abilities=None
    ):

      self.name = name
      self.character_class = character_class

      self.max_health = health
      self.health = health

      self.attack = attack
      self.defense = defense
      self.speed = speed

      self.resistances = resistances if resistances else {
         SpellSchool.PHYSICAL: 0,
         SpellSchool.ARCANE: 0,
         SpellSchool.FIRE: 0,
         SpellSchool.FROST: 0,
         SpellSchool.HOLY: 0,
         SpellSchool.NATURE: 0,
         SpellSchool.SHADOW: 0,
      }


      self.abilities = abilities if abilities else []
      self.active_effects = []

  def is_alive(self):
     return self.health > 0

  def take_damage(self, amount):
    damage = max(0, amount - self.defense)
    self.health = max(0, self.health - damage)
    return damage

  def add_effect(self, effect):
     self.active_effects.append(effect)

  def remove_effect(self, effect):
     if effect in self.active_effects:
        self.active_effects.remove(effect)

  def update_effects(self):
    for effect in self.active_effects:
      effect.reduce_duration()

      self.active_effects = [
         effect for effect in self.active_effects
         if effect.is_active()
        ]

