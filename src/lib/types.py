from enum import Enum

class SpellSchool(Enum):
  PHYSICAL = "Physical"
  ARCANE = "Arcane"
  FIRE = "Fire"
  FROST = "Frost"
  HOLY = "Holy"
  NATURE = "Nature"
  SHADOW = "Shadow"

class EffectType(Enum):
  BUFF = "Buff"
  DEBUFF = "Debuff"
  DAMAGE_OVER_TIME = "Damage Over Time"
  IMMUNITY = "Immunity"

class TargetType(Enum):
  SELF = "Self"
  SINGLE_ALLY = "Single Ally"
  ALL_ALLIES = "All Allies"
  SINGLE_ENEMY = "Single Enemy"
  ALL_ENEMIES = "All Enemies"

class EffectCategory(Enum):
  PHYSICAL = "Physical"
  MAGICAL = "Magical"
  CURSE = "Curse"
  DISEASE = "Disease"
  POISON = "Poison"