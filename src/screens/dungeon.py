import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GRAY
from .base import Screen
from .widgets import draw_status_lines, draw_text
from encounters import generate_encounter


class DungeonScreen(Screen):
  def handle_input(self, event, game):
    if event.key == pygame.K_RETURN:
      game.current_enemies = generate_encounter(
        game.selected_dungeon, game.current_encounter + 1
      )
      game.state = GameState.ENCOUNTER

    elif event.key == pygame.K_ESCAPE:
      game.state = GameState.DUNGEON_SELECTION

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 64)
    text_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 28)

    draw_text(screen, title_font, game.selected_dungeon, WHITE, (500, 80))
    draw_text(
      screen, text_font,
      f"Encounter {game.current_encounter + 1} / {game.total_encounters}",
      GOLD, (500, 150)
    )

    # Damage carries over between fights, so show where the party stands
    draw_text(screen, info_font, "Your Party", GRAY, (500, 230))
    draw_status_lines(screen, text_font, game.party, top=270, spacing=45)

    draw_text(
      screen, text_font, "A group of enemies awaits...", WHITE, (500, 450)
    )
    draw_text(
      screen, info_font, "Enter: Begin Encounter | Escape: Back", GRAY, (500, 620)
    )
