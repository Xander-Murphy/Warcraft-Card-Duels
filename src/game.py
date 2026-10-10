import pygame

from states import GameState
from lib.colors import BACKGROUND
from screens.main_menu import MainMenuScreen
from screens.team_selection import TeamSelectionScreen
from screens.dungeon_selection import DungeonSelectionScreen
from screens.dungeon import DungeonScreen
from screens.encounter import EncounterScreen
from hero_data import *
from screens.combat import CombatScreen


class Game:
  def __init__(self, screen):
    self.screen = screen
    self.running = True
    self.state = GameState.MAIN_MENU

    # shared game data — not tied to any one screen
    self.available_heroes = [KORYNE, GENJO, SCATTER, BRAEKS]
    self.selected_heroes = []  # heroes the player picks for their team
    self.party = []  # cloned copies of those heroes used in a dungeon run

    self.available_dungeons = ["Ragefire Chasm", "Wailing Caverns", "The Deadmines"]
    self.selected_dungeon: str | None = None

    self.current_encounter = 0
    self.total_encounters = 3
    self.current_enemies = []

    # one screen instance per state; each owns its own UI-only state
    # (cursor position, etc.) and reads/writes the shared data above.
    # ENCOUNTER and COMBAT aren't built yet, so they're left out for now —
    # reaching those states currently does nothing rather than crashing.
    self.screens = {
      GameState.MAIN_MENU: MainMenuScreen(),
      GameState.TEAM_SELECTION: TeamSelectionScreen(),
      GameState.DUNGEON_SELECTION: DungeonSelectionScreen(),
      GameState.DUNGEON: DungeonScreen(),
      GameState.ENCOUNTER: EncounterScreen(),
      GameState.COMBAT: CombatScreen()
    }

  def start_run(self):
    """Begin a dungeon run with fresh copies of the selected heroes."""
    self.party = [hero.clone() for hero in self.selected_heroes]
    self.current_encounter = 0
    self.current_enemies = []

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False

      elif event.type == pygame.KEYDOWN:
        current_screen = self.screens.get(self.state)
        if current_screen:
          current_screen.handle_input(event, self)

  def update(self):
    pass

  def draw(self):
    self.screen.fill(BACKGROUND)

    current_screen = self.screens.get(self.state)
    if current_screen:
      current_screen.draw(self.screen, self)

  def run(self):
    clock = pygame.time.Clock()

    while self.running:
      self.handle_events()
      self.update()
      self.draw()

      pygame.display.flip()
      clock.tick(60)
