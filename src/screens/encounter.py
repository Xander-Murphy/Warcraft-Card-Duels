import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GRAY
from .base import Screen
from .widgets import draw_status_lines, draw_text


class EncounterScreen(Screen):
  def handle_input(self, event, game):
    if event.key == pygame.K_RETURN:
      game.start_combat()
      game.state = GameState.COMBAT

    elif event.key == pygame.K_ESCAPE:
      game.state = GameState.DUNGEON

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 64)
    text_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 28)

    draw_text(screen, title_font, "Enemy Encounter", WHITE, (500, 80))
    draw_text(screen, info_font, game.selected_dungeon, GOLD, (500, 140))

    draw_status_lines(screen, text_font, game.current_enemies, top=210, spacing=50)

    draw_text(screen, info_font, "Your Party", GRAY, (500, 400))
    draw_status_lines(screen, info_font, game.party, top=440, spacing=40)

    draw_text(
      screen, info_font, "Enter: Begin Combat | Escape: Back", GRAY, (500, 620)
    )
