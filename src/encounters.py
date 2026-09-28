import random

from enemy_data import *

RAGEFIRE_ENCOUNTERS = {
  1: [RAGEFIRE_TROG, RAGEFIRE_SHAMAN],
  2: [EARTHBORER, MOLTEN_ELEMENTAL],
  3: [SEARING_BLADE_CULTIST, SEARING_BLADE_ENFORCER, SEARING_BLADE_WARLOCK]
}

WAILING_CAVERNS_ENCOUNTERS = {
  1: [DEVIATE_GUARDIAN, DEVIATE_RAVAGER ,DEVIATE_RAVAGER],
  2: [DEVIATE_SHAMBLER, DEVIATE_VIPER, DEVIATE_LASHER],
  3: [DRUID_OF_THE_FANG, DEVIATE_SHAMBLER, DRUID_OF_THE_FANG]
}

DEADMINES_ENCOUNTERS = {
  1: [DEFIAS_MINER, DEFIAS_STRIP_MINER],
  2: [GOBLIN_CRAFTSMAN, GOBLIN_ENGINEER, GOBLIN_WOODCARVER],
  3: [DEFIAS_BLACKGUARD, DEFIAS_EVOKER, DEFIAS_WIZARD, DEFIAS_PIRATE, DEFIAS_TASKMASTER, DEFIAS_SQUALLSHAPER],
}

def generate_encounter(dungeon, encounter_number):
  match dungeon:
    case "Ragefire Chasm": encounter_pool = RAGEFIRE_ENCOUNTERS
    case "Wailing Caverns": encounter_pool = WAILING_CAVERNS_ENCOUNTERS
    case "The Deadmines": encounter_pool = DEADMINES_ENCOUNTERS

  enemies = encounter_pool.get(encounter_number, [])

  if not enemies:
    return []

  enemy_count = random.randint(2, 3)

  return random.choices(enemies, k=enemy_count)