from enum import Enum, auto

class GameState(Enum):
  MAIN_MENU = auto()
  TEAM_SELECTION = auto()
  DUNGEON_SELECTION = auto()
  DUNGEON = auto()
  ENCOUNTER = auto()
  COMBAT = auto()
  VICTORY = auto()
  GAME_OVER = auto()
  GAME_WON = auto()