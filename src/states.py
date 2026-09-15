from enum import Enum, auto

class GameState(Enum):
  MAIN_MENU = auto()
  TEAM_SELECTION = auto()
  ENCOUNTER = auto()
  COMBAT = auto()
  VICTORY = auto()
  GAME_OVER = auto()
  GAME_WON = auto()