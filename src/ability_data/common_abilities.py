from abilities import Ability
from ability_effects import DamageEffect
from lib.types import SpellSchool, TargetType

# Anyone can use this at any time, whatever their abilities' cooldowns.
BASIC_ATTACK = Ability(
  "Basic Attack",
  "Deals physical damage to one enemy.",
  15,
  0,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)
