# Architecture & Design

## Architecture

The game will be divided into several major systems:

```text
                     Game Manager
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
     Hero System     Combat System   Encounter System
          |               |               |
          v               v               v
      Abilities        Enemies          Bosses
                          |
                          v
                          UI
```

### Game Manager

Controls overall game flow and manages game states such as starting, playing, and ending the game.

### Hero System

Manages heroes, their statistics, classes, specializations, and abilities. It also manages the player's team of three heroes.

### Combat System

Handles turn order, player and enemy actions, damage, ability effects, and victory/defeat conditions.

### Enemy System

Manages enemy statistics, types, and behaviors. Bosses can extend the basic enemy functionality.

### Encounter System

Creates enemy encounters, manages progression, and controls increasingly difficult battles and boss encounters.

### UI

Displays game information, character statistics, available actions, and game states while handling player input.

## Design

### Encapsulation

Each class manages its own data and behavior, keeping implementation details contained within the appropriate system.

### Separation of Concerns

Game management, combat, characters, encounters, and UI are kept separate so changes to one system have minimal impact on others.

### Inheritance

```text
Character
├── Hero
└── Enemy
    └── Boss
```

Shared character functionality can be placed in a base `Character` class while allowing heroes, enemies, and bosses to have specialized behavior.

### Composition

Heroes will contain their abilities, allowing different heroes to have different combinations of abilities without creating unnecessary classes.

```text
Hero
└── Abilities
    ├── Ability
    ├── Ability
    └── Ability
```

### State Pattern

The State Pattern will separate major game states and allow the Game Manager to transition between them cleanly.

### Strategy Pattern

The Strategy Pattern can be used to give different enemy types unique decision-making behaviors without changing the core combat system.

## Design Goals

* Keep systems modular and organized.
* Make new heroes, abilities, enemies, and encounters easy to add.
* Minimize dependencies between systems.
* Make individual components easier to test and debug.
* Provide a foundation that can support the game's planned features.
