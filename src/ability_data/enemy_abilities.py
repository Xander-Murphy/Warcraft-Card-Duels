from abilities import Ability
from ability_effects import DamageEffect
from lib.types import SpellSchool, TargetType

TROG_SMASH = Ability(
  "Trog Smash",
  "Deals physical damage to one enemy.",
  20,
  1,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

SHAMAN_LIGHTNING = Ability(
  "Lightning Bolt",
  "Deals nature damage to one enemy.",
  25,
  1,
  TargetType.SINGLE_ENEMY,
  SpellSchool.NATURE,
  effects=[DamageEffect()]
)

EARTHBORER_STRIKE = Ability(
  "Earthborer Strike",
  "Deals physical damage to one enemy.",
  25,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)


MOLTEN_BLAST = Ability(
  "Molten Blast",
  "Deals fire damage to one enemy.",
  30,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.FIRE,
  effects=[DamageEffect()]
)

