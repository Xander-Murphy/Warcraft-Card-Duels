from heroes import Hero
from ability_data.hero_abilities import *
'''
This houses all hero data
NAME = Hero("Name", "Class", "Spec", health, attack, defense, speed)
'''

KORYNE = Hero("Koryne", "Mage", "Arcane", 75, 26, 0, 7, abilities=[ARCANE_BLAST, ARCANE_EXPLOSION, ARCANE_BARRIER])
GENJO = Hero("Genjo", "Rogue", "Subtlety", 85, 23, 1, 9, abilities=[BACKSTAB, EVASION, CLOAK_OF_SHADOWS])
SCATTER = Hero("Scatter", "Hunter", "Survival", 95, 21, 2, 7, abilities=[SERPENT_STING, MULTI_SHOT, SURVIVAL_INSTINCTS])
BRAEKS = Hero("Braeks", "Warrior", "Fury", 115, 19, 3, 5, abilities=[HEROIC_STRIKE, BERSERKER_RAGE, WHIRLWIND])

