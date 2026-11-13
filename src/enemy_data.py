from enemies import Enemy
from ability_data.enemy_abilities import *
from lib.types import SpellSchool
'''
This houses all enemy data, comment above says the dungeon they are for
NAME = Enemy("Name", "Class", Health, Attack, Defense, Speed)

These are prototypes: never mutate them. Use .clone() to get a copy to play with.
'''
### Ragefire Chasm
 
RAGEFIRE_TROG = Enemy("Ragefire Trog", "Physical", 40, 8, 0, 4, abilities=[TROG_SMASH, HEADBUTT])
RAGEFIRE_SHAMAN = Enemy("Ragefire Shaman", "Caster", 35, 10, 0, 5, abilities=[SHAMAN_LIGHTNING, FLAME_LASH])
 
EARTHBORER = Enemy("Earthborer", "Physical", 45, 12, 2, 5, abilities=[EARTHBORER_STRIKE, TUNNEL_CHARGE])
MOLTEN_ELEMENTAL = Enemy("Molten Elemental", "Caster", 50, 10, 2, 4, resistances={SpellSchool.FIRE: 25, SpellSchool.FROST: -10}, abilities=[MOLTEN_BLAST, MAGMA_SPLASH])
 
SEARING_BLADE_CULTIST = Enemy("Searing Blade Cultist", "Physical", 50, 13, 1, 6, abilities=[SEARING_SLASH, RITUAL_BLADE])
SEARING_BLADE_WARLOCK = Enemy("Searing Blade Warlock", "Caster", 44, 16, 0, 7, abilities=[IMMOLATE, CURSE_OF_AGONY])
SEARING_BLADE_ENFORCER = Enemy("Searing Blade Enforcer", "Physical", 60, 11, 3, 5, abilities=[SHIELD_SLAM, CLEAVE])
 
TARAGAMAN_THE_HUNGERER = Enemy("Taragaman the Hungerer", "Physical", 170, 16, 3, 5)
 
### Wailing Caverns
 
DEVIATE_RAVAGER = Enemy("Deviate Ravager", "Physical",46, 11, 1, 5, abilities=[RAVAGE, RENDING_BITE])
DEVIATE_GUARDIAN = Enemy("Deviate Guardian", "Physical",48, 12, 3, 4, abilities=[CRUSHING_BLOW, GUARDIAN_SLAM])
 
DEVIATE_VIPER = Enemy("Deviate Viper", "Physical", 50, 13, 2, 6, abilities=[LUNGE, POISON_BITE])
DEVIATE_SHAMBLER = Enemy("Deviate Shambler", "Physical", 55, 12, 3, 4, abilities=[THORN_LASH, TRAMPLE])
DEVIATE_LASHER = Enemy("Deviate Lasher", "Physical", 44, 11, 0, 5, abilities=[LASH, WHIRLING_VINES])
 
DRUID_OF_THE_FANG = Enemy("Druid of the Fang", "Caster", 60, 15, 2, 6, abilities=[FANG_MOONFIRE, ENTANGLING_ROOTS])
 
MUTANUS_THE_DEVOURER = Enemy("Mutanus the Devourer", "Physical", 200, 18, 4, 5)
 
### The Deadmines
 
DEFIAS_MINER = Enemy("Defias Miner", "Physical", 47, 12, 0, 5, abilities=[PICKAXE_STRIKE, SUNDER_PICK])
DEFIAS_STRIP_MINER = Enemy("Defias Strip Miner", "Physical", 52, 12, 1, 4, abilities=[HEAVY_SWING, CAVE_IN])
 
GOBLIN_WOODCARVER = Enemy("Goblin Woodcarver", "Physical", 55, 14, 2, 4, abilities=[AXE_CHOP, SPLINTER_SPRAY])
GOBLIN_CRAFTSMAN = Enemy("Goblin Craftsman", "Physical", 52, 15, 1, 6, abilities=[WRENCH_SMACK, SHODDY_BOMB])
GOBLIN_ENGINEER = Enemy("Goblin Engineer",  "Caster", 54, 16, 3, 5, abilities=[FLAMETHROWER, ELECTRIFIED_NET])
 
DEFIAS_BLACKGUARD = Enemy("Defias Blackguard", "Physical", 62, 14, 4, 5, abilities=[DIRTY_STRIKE, HAMSTRING])
DEFIAS_TASKMASTER = Enemy("Defias Taskmaster", "Physical", 58, 15, 2, 6, abilities=[WHIP_CRACK, LASH_OUT])
DEFIAS_PIRATE = Enemy("Defias Pirate", "Physical", 58, 17, 2, 6, abilities=[CUTLASS_SLASH, PISTOL_SHOT])
DEFIAS_SQUALLSHAPER = Enemy("Defias Squallshaper", "Caster", 54, 21, 1, 7, abilities=[FROSTBOLT, SQUALL])
DEFIAS_WIZARD = Enemy("Defias Wizard", "Caster", 52, 19, 1, 7, abilities=[FIREBALL, MANA_BURN])
DEFIAS_EVOKER = Enemy("Defias Evoker", "Caster", 50, 18, 0, 7, abilities=[FIRE_BLAST, SHADOW_WORD_PAIN])
 
EDWIN_VANCLEEF = Enemy("Edwin VanCleef", "Physical", 235, 21, 4, 6)