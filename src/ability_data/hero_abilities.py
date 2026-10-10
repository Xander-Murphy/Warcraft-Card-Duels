from abilities import Ability
from ability_effects import DamageEffect, ApplyStatusEffect
from lib.types import SpellSchool, TargetType
import effects_data as fx

# Koryne - Mage / Arcane
ARCANE_BLAST = Ability(
  "Arcane Blast",
  "Launch a powerful arcane projectile at an enemy",
  30,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.ARCANE,
  effects=[DamageEffect()]
)

ARCANE_EXPLOSION = Ability(
  "Arcane Explosion",
  "Deals arcane damage to all enemies.",
  20,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.ARCANE,
  effects=[DamageEffect()]
)

ARCANE_BARRIER = Ability(
  "Arcane Barrier",
  "Grants resistance to all schools",
  15,
  3,
  TargetType.SELF,
  SpellSchool.ARCANE,
  effects=[ApplyStatusEffect(fx.ARCANE_BARRIER)]
)

# Genjo - Rogue / Subtlety
BACKSTAB = Ability(
  "Backstab",
  "Deals physical damage to one enemy",
  25,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

EVASION = Ability(
  "Evasion",
  "Become immune to physical damage for one turn",
  0,
  4,
  TargetType.SELF,
  priority=10,
  effects=[ApplyStatusEffect(fx.PHYSICAL_IMMUNITY)]
)

# TODO: Cloak should also remove magical effects (needs a DispelEffect)
CLOAK_OF_SHADOWS = Ability(
  "Cloak of Shadows",
  "Become immune to magical damage and remove magical effects",
  0,
  4,
  TargetType.SELF,
  priority=10,
  effects=[ApplyStatusEffect(fx.MAGICAL_IMMUNITY)]
)

# Scatter Hunter / Survival
SERPENT_STING = Ability(
  "Serpent Sting",
  "Deals physical damage and applies poison.",
  20,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect(), ApplyStatusEffect(fx.POISON)]
)

MULTI_SHOT = Ability(
  "Multi-Shot",
  "Deals physical damage to all enemies",
  15,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

SURVIVAL_INSTINCTS = Ability(
  "Survival Instincts",
  "Grants increased defense",
  7,
  3,
  TargetType.SELF,
  SpellSchool.PHYSICAL,
  effects=[ApplyStatusEffect(fx.SURVIVAL_INSTINCTS)]
)

# Braeks Warrior / Fury 
HEROIC_STRIKE = Ability(
  "Heroic Strike",
  "Deals physical damage to one enemy",
  25,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

BERSERKER_RAGE = Ability(
  "Berserker Rage",
  "Increase offensive power for the next three abilities",
  10,
  4,
  TargetType.SELF,
  priority=10,
  effects=[ApplyStatusEffect(fx.BERSERKER_RAGE)]
)

WHIRLWIND = Ability(
  "Whirlwind",
  "Deals physical damage to all enemies",
  15,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)
