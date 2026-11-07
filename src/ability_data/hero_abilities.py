from abilities import Ability
from ability_effects import ApplyStatusEffect, DamageEffect, HealEffect
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

# Liora - Priest / Holy
FLASH_HEAL = Ability(
  "Flash Heal",
  "Heals one ally",
  30,
  1,
  TargetType.SINGLE_ALLY,
  SpellSchool.HOLY,
  effects=[HealEffect()]
)

PRAYER_OF_HEALING = Ability(
  "Prayer of Healing",
  "Heals the whole party",
  18,
  3,
  TargetType.ALL_ALLIES,
  SpellSchool.HOLY,
  effects=[HealEffect()]
)

SMITE = Ability(
  "Smite",
  "Deals holy damage to one enemy",
  22,
  1,
  TargetType.SINGLE_ENEMY,
  SpellSchool.HOLY,
  effects=[DamageEffect()]
)

# Torvald - Paladin / Protection
JUDGMENT = Ability(
  "Judgment",
  "Deals holy damage to one enemy",
  24,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.HOLY,
  effects=[DamageEffect()]
)

CONSECRATION = Ability(
  "Consecration",
  "Deals holy damage to all enemies, then burns them for 2 rounds",
  8,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.HOLY,
  effects=[DamageEffect(), ApplyStatusEffect(fx.CONSECRATION)]
)

DEVOTION_AURA = Ability(
  "Devotion Aura",
  "Grants the whole party increased defense for 2 rounds",
  4,
  4,
  TargetType.ALL_ALLIES,
  SpellSchool.HOLY,
  effects=[ApplyStatusEffect(fx.DEVOTION_AURA)]
)

# Vesk - Warlock / Affliction
SHADOW_BOLT = Ability(
  "Shadow Bolt",
  "Deals shadow damage to one enemy",
  26,
  1,
  TargetType.SINGLE_ENEMY,
  SpellSchool.SHADOW,
  effects=[DamageEffect()]
)

CORRUPTION = Ability(
  "Corruption",
  "Deals shadow damage to one enemy every round for 4 rounds",
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.SHADOW,
  effects=[ApplyStatusEffect(fx.CORRUPTION)]
)

CURSE_OF_WEAKNESS = Ability(
  "Curse of Weakness",
  "Lowers one enemy's attack for 3 rounds",
  10,
  4,
  TargetType.SINGLE_ENEMY,
  SpellSchool.SHADOW,
  effects=[ApplyStatusEffect(fx.CURSE_OF_WEAKNESS)]
)

# Tamaru - Shaman / Elemental
CHAIN_LIGHTNING = Ability(
  "Chain Lightning",
  "Deals nature damage to all enemies",
  16,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.NATURE,
  effects=[DamageEffect()]
)

FLAME_SHOCK = Ability(
  "Flame Shock",
  "Deals fire damage to one enemy, then burns it for 3 rounds",
  14,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.FIRE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.FLAME_SHOCK)]
)

HEALING_WAVE = Ability(
  "Healing Wave",
  "Heals one ally",
  22,
  3,
  TargetType.SINGLE_ALLY,
  SpellSchool.NATURE,
  effects=[HealEffect()]
)
