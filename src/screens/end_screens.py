import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GREEN, GRAY, RED
from .base import Screen


class EndScreen(Screen):
  """A full-screen result with a short party summary; Enter moves on.

  Subclasses only say what to show and where Enter leads, so a new ending
  (for example a boss victory) is one more small subclass.
  """

  title: str = ""
  title_color = WHITE
  next_state = GameState.MAIN_MENU
  prompt = "Enter: Continue"

  def subtitle(self, game) -> str:
    return ""

  def handle_input(self, event, game):
    if event.key == pygame.K_RETURN:
      game.state = self.next_state

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 96)
    text_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 28)

    self._text(screen, title_font, self.title, self.title_color, (500, 120))
    self._text(screen, text_font, self.subtitle(game), GOLD, (500, 200))

    for index, hero in enumerate(game.party):
      status = "Defeated" if not hero.is_alive() else f"{hero.health}/{hero.max_health} HP"
      color = GRAY if not hero.is_alive() else WHITE
      self._text(
        screen, text_font, f"{hero.name} - {status}", color, (500, 300 + index * 50)
      )

    self._text(screen, info_font, self.prompt, GRAY, (500, 620))

  def _text(self, screen, font, text, color, center):
    rendered = font.render(text, True, color)
    screen.blit(rendered, rendered.get_rect(center=center))


class GameOverScreen(EndScreen):
  title = "GAME OVER"
  title_color = RED
  next_state = GameState.MAIN_MENU
  prompt = "Enter: Main Menu"

  def subtitle(self, game) -> str:
    cleared = game.current_encounter
    return f"Your party fell in {game.selected_dungeon} ({cleared}/{game.total_encounters} cleared)"


class GameWonScreen(EndScreen):
  title = "DUNGEON CLEARED"
  title_color = GREEN
  next_state = GameState.DUNGEON_SELECTION
  prompt = "Enter: Choose Another Dungeon"

  def subtitle(self, game) -> str:
    return f"You conquered {game.selected_dungeon}!"