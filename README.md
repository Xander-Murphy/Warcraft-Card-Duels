# Warcraft-Card-Duels
This is my individual project for ASE 420, ASE 330 and serves as a baseline for my Capstone project.

## Project Description

A Python-based turn-based RPG where players build a team of three heroes with unique abilities and fight groups of enemies before facing powerful bosses.

## Problem

Players want an engaging turn-based RPG experience with varied heroes, abilities, enemies, and challenging encounters.

## Solution

The game will allow players to:

* Build a team of 3 heroes
* Choose from a variety of heroes with different abilities
* Fight randomly generated groups of 1–3 enemies
* Progress through increasingly difficult encounters
* Face powerful boss enemies

## Technology

* **Python** — Primary programming language
* **Pygame** — Game interface, graphics, and user input
* **uv** — Python project and dependency management

## Setup

### Requirements

* Python
* uv
* Pygame

### Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Xander-Murphy/Warcraft-Card-Duels
cd <project-directory>
```

Create the virtual environment and install the project dependencies:

```bash
uv venv
uv add pygame
```

### Running the Game

Run the game with:

```bash
uv run src/game.py
```

> **Note:** The game is currently under development, so the final game entry point may change as the project develops.

## Current Plan

The project is divided into two 5-week sprints.

### Sprint 1 — Foundation & Core Combat

**Goal:** Build the foundation of the game and establish a modular combat architecture.

| Week | Milestone                  |
| ---- | -------------------------- |
| 4    | Project setup              |
| 5    | Game states                |
| 6    | Characters                 |
| 7    | Turns and actions          |
| 8    | Win conditions and testing |

**Sprint 1 Features:**

* Hero/team system
* Core combat system
* Character statistics
* Turn-based combat
* Basic combat actions
* Victory and defeat conditions

**Sprint 1 Deliverable:** A playable combat environment demonstrating heroes, enemies, turn-based combat, displayed statistics, and victory/defeat conditions.

### Sprint 2 — Heroes, Abilities & Progression

**Goal:** Turn the combat prototype into the intended gameplay experience.

| Week | Milestone                            |
| ---- | ------------------------------------ |
| 10   | New heroes                           |
| 11   | Team selection                       |
| 12   | Hero abilities                       |
| 13   | Enemy types and encounters           |
| 14   | Bosses, balancing, and final testing |

**Sprint 2 Features:**

* Expanded hero/team system
* Unique hero abilities
* Multiple enemy types
* Random encounters
* Encounter progression
* Boss encounters

**Sprint 2 Deliverable:** A complete playable experience where players select a team, use unique abilities, fight varied enemy encounters, progress through the game, and face stronger bosses.
