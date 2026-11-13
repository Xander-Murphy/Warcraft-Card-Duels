from abilities import Ability
from ability_effects import ApplyStatusEffect, DamageEffect
from lib.types import SpellSchool, TargetType
import effects_data as fx

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


# --- Week 12: every regular enemy has two abilities -------------------------

HEADBUTT = Ability(
  'Headbutt',
  'Slams its head into one hero',
  22,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

FLAME_LASH = Ability(
  'Flame Lash',
  'Lashes one hero with fire, leaving a burn',
  10,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.FIRE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.BURN)]
)

TUNNEL_CHARGE = Ability(
  'Tunnel Charge',
  'Bursts up beneath the whole party',
  10,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

MAGMA_SPLASH = Ability(
  'Magma Splash',
  'Splashes the whole party with burning magma',
  8,
  4,
  TargetType.ALL_ENEMIES,
  SpellSchool.FIRE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.BURN)]
)

SEARING_SLASH = Ability(
  'Searing Slash',
  'A heavy slash at one hero',
  22,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

RITUAL_BLADE = Ability(
  'Ritual Blade',
  'Cuts one hero, leaving them bleeding',
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect(), ApplyStatusEffect(fx.BLEED)]
)

IMMOLATE = Ability(
  'Immolate',
  'Sets one hero alight',
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.FIRE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.BURN)]
)

CURSE_OF_AGONY = Ability(
  'Curse of Agony',
  'Curses one hero with shadow pain over time',
  6,
  4,
  TargetType.SINGLE_ENEMY,
  SpellSchool.SHADOW,
  effects=[DamageEffect(), ApplyStatusEffect(fx.AGONY)]
)

SHIELD_SLAM = Ability(
  'Shield Slam',
  'Slams one hero with a shield',
  22,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

CLEAVE = Ability(
  'Cleave',
  'Swings through the whole party',
  12,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

RAVAGE = Ability(
  'Ravage',
  'Mauls one hero',
  20,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

RENDING_BITE = Ability(
  'Rending Bite',
  'Bites one hero, leaving them bleeding',
  10,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect(), ApplyStatusEffect(fx.BLEED)]
)

CRUSHING_BLOW = Ability(
  'Crushing Blow',
  'A crushing hit on one hero',
  20,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

GUARDIAN_SLAM = Ability(
  'Guardian Slam',
  'Slams one hero and weakens their armor',
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect(), ApplyStatusEffect(fx.ARMOR_BREAK)]
)

LUNGE = Ability(
  'Lunge',
  'Lunges at one hero',
  22,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

POISON_BITE = Ability(
  'Poison Bite',
  'Bites one hero and poisons them',
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect(), ApplyStatusEffect(fx.POISON)]
)

THORN_LASH = Ability(
  'Thorn Lash',
  'Lashes one hero with thorns',
  22,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

TRAMPLE = Ability(
  'Trample',
  'Tramples the whole party',
  11,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

LASH = Ability(
  'Lash',
  'Whips one hero with a vine',
  20,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

WHIRLING_VINES = Ability(
  'Whirling Vines',
  'Whips the whole party with vines',
  10,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

FANG_MOONFIRE = Ability(
  'Moonfire',
  'Burns one hero with arcane moonlight over time',
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.ARCANE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.MOONFIRE)]
)

ENTANGLING_ROOTS = Ability(
  'Entangling Roots',
  'Roots one hero, slowing them',
  10,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.NATURE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.ENTANGLED)]
)

PICKAXE_STRIKE = Ability(
  'Pickaxe Strike',
  'Swings a pickaxe at one hero',
  20,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

SUNDER_PICK = Ability(
  'Sunder Pick',
  "Cracks one hero's armor",
  10,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect(), ApplyStatusEffect(fx.ARMOR_BREAK)]
)

HEAVY_SWING = Ability(
  'Heavy Swing',
  'A heavy swing at one hero',
  22,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

CAVE_IN = Ability(
  'Cave-In',
  'Brings rocks down on the whole party',
  10,
  4,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

AXE_CHOP = Ability(
  'Axe Chop',
  'Chops at one hero',
  24,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

SPLINTER_SPRAY = Ability(
  'Splinter Spray',
  'Sprays the whole party with splinters',
  11,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

WRENCH_SMACK = Ability(
  'Wrench Smack',
  'Smacks one hero with a wrench',
  22,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

SHODDY_BOMB = Ability(
  'Shoddy Bomb',
  'Throws a bomb at the whole party',
  12,
  4,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

FLAMETHROWER = Ability(
  'Flamethrower',
  'Scorches one hero, leaving a burn',
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.FIRE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.BURN)]
)

ELECTRIFIED_NET = Ability(
  'Electrified Net',
  'Nets one hero, slowing them',
  10,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.NATURE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.ENTANGLED)]
)

DIRTY_STRIKE = Ability(
  'Dirty Strike',
  'A dirty hit on one hero',
  26,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

HAMSTRING = Ability(
  'Hamstring',
  'Cuts one hero, slowing them',
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect(), ApplyStatusEffect(fx.HAMSTRUNG)]
)

WHIP_CRACK = Ability(
  'Whip Crack',
  'Cracks a whip at one hero',
  24,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

LASH_OUT = Ability(
  'Lash Out',
  'Lashes out at the whole party',
  12,
  3,
  TargetType.ALL_ENEMIES,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

CUTLASS_SLASH = Ability(
  'Cutlass Slash',
  'Slashes one hero with a cutlass',
  26,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

PISTOL_SHOT = Ability(
  'Pistol Shot',
  'Shoots one hero',
  18,
  1,
  TargetType.SINGLE_ENEMY,
  SpellSchool.PHYSICAL,
  effects=[DamageEffect()]
)

FROSTBOLT = Ability(
  'Frostbolt',
  'Hits one hero with frost, chilling them',
  16,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.FROST,
  effects=[DamageEffect(), ApplyStatusEffect(fx.CHILLED)]
)

SQUALL = Ability(
  'Squall',
  'Hits the whole party with icy wind',
  10,
  4,
  TargetType.ALL_ENEMIES,
  SpellSchool.FROST,
  effects=[DamageEffect()]
)

FIREBALL = Ability(
  'Fireball',
  'Hurls fire at one hero, leaving a burn',
  18,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.FIRE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.BURN)]
)

MANA_BURN = Ability(
  'Mana Burn',
  'Drains one hero, lowering their attack',
  12,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.ARCANE,
  effects=[DamageEffect(), ApplyStatusEffect(fx.WEAKENED)]
)

FIRE_BLAST = Ability(
  'Fire Blast',
  'Blasts one hero with fire',
  20,
  2,
  TargetType.SINGLE_ENEMY,
  SpellSchool.FIRE,
  effects=[DamageEffect()]
)

SHADOW_WORD_PAIN = Ability(
  'Shadow Word: Pain',
  'Curses one hero with shadow pain over time',
  8,
  3,
  TargetType.SINGLE_ENEMY,
  SpellSchool.SHADOW,
  effects=[DamageEffect(), ApplyStatusEffect(fx.AGONY)]
)
