from effects import StatusEffect
from lib.types import EffectType, EffectCategory, SpellSchool, Stat

'''
Status effect prototypes. Like hero/enemy/ability data, these are never applied
directly: ApplyStatusEffect clones them onto the target.

StatusEffect(name, type, category, magnitude, duration, schools, stat)
'''

POISON = StatusEffect(
  "Poison",
  EffectType.DAMAGE_OVER_TIME,
  EffectCategory.POISON,
  10,
  3,
  damage_school=SpellSchool.NATURE
)

ARMOR_BREAK = StatusEffect(
  "Armor Break",
  EffectType.DEBUFF,
  EffectCategory.PHYSICAL,
  5,
  2,
  stat=Stat.DEFENSE
)

ARCANE_VULNERABILITY = StatusEffect(
  "Arcane Vulnerability",
  EffectType.DEBUFF,
  EffectCategory.MAGICAL,
  25,
  3,
  [SpellSchool.ARCANE],
  Stat.RESISTANCE
)

PHYSICAL_IMMUNITY = StatusEffect(
  "Physical Immunity",
  EffectType.IMMUNITY,
  EffectCategory.PHYSICAL,
  0,
  1,
  [SpellSchool.PHYSICAL]
)

MAGICAL_IMMUNITY = StatusEffect(
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
  3,
  stat=Stat.ATTACK
)

# Durations for the two buffs below are placeholders until balancing (week 14).
ARCANE_BARRIER = StatusEffect(
  "Arcane Barrier",
  EffectType.BUFF,
  EffectCategory.MAGICAL,
  15,
  2,
  list(SpellSchool),
  Stat.RESISTANCE
)

SURVIVAL_INSTINCTS = StatusEffect(
  "Survival Instincts",
  EffectType.BUFF,
  EffectCategory.PHYSICAL,
  7,
  2,
  stat=Stat.DEFENSE
)
