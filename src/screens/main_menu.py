import pygame

from states import GameState
from lib.colors import WHITE, GOLD
from .base import Screen


class MainMenuScreen(Screen):
  def __init__(self):
    self.menu_selection = 0  # 0 = Start Game, 1 = Quit Game

  def handle_input(self, event, game):
    match event.key:
      case pygame.K_UP | pygame.K_w:
        self.menu_selection -= 1

      case pygame.K_DOWN | pygame.K_s:
        self.menu_selection += 1

      case pygame.K_RETURN:
        self._confirm_selection(game)

    self.menu_selection %= 2

  def _confirm_selection(self, game):
    if self.menu_selection == 0:
      game.state = GameState.TEAM_SELECTION
    elif self.menu_selection == 1:
      game.running = False

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 72)
    button_font = pygame.font.Font(None, 42)

    title = title_font.render("Warcraft Card Duels", True, WHITE)

    start_color = GOLD if self.menu_selection == 0 else WHITE
    quit_color = GOLD if self.menu_selection == 1 else WHITE

    start_text = button_font.render("Start Game", True, start_color)
    quit_text = button_font.render("Quit Game", True, quit_color)

    title_rect = title.get_rect(center=(500, 150))
    start_rect = start_text.get_rect(center=(500, 350))
    quit_rect = quit_text.get_rect(center=(500, 450))

    screen.blit(title, title_rect)
    screen.blit(start_text, start_rect)
    screen.blit(quit_text, quit_rect)
