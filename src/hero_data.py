from heroes import Hero
from ability_data.hero_abilities import *
from lib.types import SpellSchool
'''
This houses all hero data
NAME = Hero("Name", "Class", "Spec", health, attack, defense, speed)

These are prototypes: never mutate them. Use .clone() to get a copy to play with.
'''

KORYNE = Hero("Koryne", "Mage", "Arcane", 75, 26, 0, 7, resistances={SpellSchool.ARCANE: 15}, abilities=[ARCANE_BLAST, ARCANE_EXPLOSION, ARCANE_BARRIER])
GENJO = Hero("Genjo", "Rogue", "Subtlety", 85, 23, 1, 9, abilities=[BACKSTAB, EVASION, CLOAK_OF_SHADOWS])
SCATTER = Hero("Scatter", "Hunter", "Survival", 95, 21, 2, 7, abilities=[SERPENT_STING, MULTI_SHOT, SURVIVAL_INSTINCTS])
BRAEKS = Hero("Braeks", "Warrior", "Fury", 115, 19, 3, 5, abilities=[HEROIC_STRIKE, BERSERKER_RAGE, WHIRLWIND])
LIORA = Hero("Liora", "Priest", "Holy", 80, 18, 0, 6, abilities=[FLASH_HEAL, PRAYER_OF_HEALING, SMITE])
TORVALD = Hero("Torvald", "Paladin", "Protection", 120, 17, 4, 4, abilities=[JUDGMENT, CONSECRATION, DEVOTION_AURA])
VESK = Hero("Vesk", "Warlock", "Affliction", 78, 24, 0, 6, abilities=[SHADOW_BOLT, CORRUPTION, CURSE_OF_WEAKNESS])
TAMARU = Hero("Tamaru", "Shaman", "Elemental", 88, 22, 1, 6, abilities=[CHAIN_LIGHTNING, FLAME_SHOCK, HEALING_WAVE])

