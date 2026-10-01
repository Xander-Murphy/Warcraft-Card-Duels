from abilities import Ability
from lib.types import SpellSchool, TargetType

# Koryne - Mage / Arcane
ARCANE_BLAST = Ability(
  "Arcane Blast",
  "Launch a powerful arcane projectile at an enemy",
  30,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.ARCANE
)

ARCANE_EXPLOSION = Ability(
  "Arcane Explosion",
  "Deals arcane damage to all enemies.",
  20,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.ARCANE
)

ARCANE_BARRIER = Ability(
  "Arcane Barrier",
  "Grants resistance to all schools",
  15,
  3,
  TargetType.SELF,
  SpellSchool.ARCANE
)

# Genjo - Rogue / Subtlety
BACKSTAB = Ability(
  "Backstab",
  "Deals physical damage to one enemy",
  25,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL
)

EVASION = Ability(
  "Evasion",
  "Become immune to physical damage for one turn",
  0,
  4,
  TargetType.SELF,
  priority=10
)

CLOAK_OF_SHADOWS = Ability(
  "Cloak of Shadows",
  "Become immune to magical damage and remove magical effects",
  0,
  4,
  TargetType.SELF,
  priority=10
)

# Scatter Hunter / Survival
SERPENT_STING = Ability(
  "Serpent Sting",
  "Deals physical damage and applies poison.",
  20,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL
)

MULTI_SHOT = Ability(
  "Multi-Shot",
  "Deals physical damage to all enemies",
  15,
  3,
  TargetType.ALL_ALLIES,
  SpellSchool.PHYSICAL
)

SURVIVAL_INSTINCTS = Ability(
  "Survival Instincts",
  "Grants increased defense",
  7,
  3,
  TargetType.SELF,
  SpellSchool.PHYSICAL,
)

# Braeks Warrior / Fury 
HEROIC_STRIKE = Ability(
  "Heroic Strike",
  "Deals physical damage to one enemy",
  25,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL
)

BERSERKER_RAGE = Ability(
  "Berserker Rage",
  "Increase offensive power for the next three abilities",
  10,
  4,
  TargetType.SELF,
  priority=10
)

WHIRLWIND = Ability(
  "Whirlwind",
  "Deals physical damage to all enemies",
  15,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL
)
