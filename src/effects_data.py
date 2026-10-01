from effects import StatusEffect
from lib.types import EffectType, EffectCategory, SpellSchool

POISON = StatusEffect(
  "Poison",
  EffectType.DAMAGE_OVER_TIME,
  EffectCategory.POISON,
  10,
  3
)

ARMOR_BREAK = StatusEffect(
  "Armor Break",
  EffectType.DEBUFF,
  EffectCategory.PHYSICAL,
  5,
  2
)

ARCANE_VULNERABILITY = StatusEffect(
  "Arcane Vulerability",
  EffectType.DEBUFF,
  EffectCategory.MAGICAL,
  25,
  3
)

PHYSICAL_IMMUNITY = StatusEffect(
  "Physical Immunity",
  EffectType.IMMUNITY,
  EffectCategory.PHYSICAL,
  0,
  1,
  [SpellSchool.PHYSICAL]
)

MAGICALL_IMMUNITY = StatusEffect(
  "Magical Immunity",
  EffectType.IMMUNITY,
  EffectCategory.MAGICAL,
  0,
  1,
  [
    SpellSchool.ARCANE,
    SpellSchool.FIRE,
    SpellSchool.FROST,
    SpellSchool.HOLY,
    SpellSchool.NATURE,
    SpellSchool.SHADOW
  ]
)

BERSERKER_RAGE = StatusEffect(
  "Berserker Rage",
  EffectType.BUFF,
  EffectCategory.PHYSICAL,
  10,
  3
)