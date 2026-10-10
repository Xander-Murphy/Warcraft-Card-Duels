from abilities import Ability
from ability_effects import DamageEffect
from lib.types import SpellSchool, TargetType

# Anyone can fall back on this when none of their abilities are ready.
BASIC_ATTACK = Ability(
  "Basic Attack",
  "Deals physical damage to one enemy.",
  15,
  0,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)
