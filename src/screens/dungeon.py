import pygame

from lib.colors import WHITE, GOLD, GRAY
from .base import Screen


class DungeonScreen(Screen):
  def handle_input(self, event, game):
    # No input handling yet — dungeon exploration isn't built out.
    pass

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 64)
    text_font = pygame.font.Font(None, 36)

    title = title_font.render("Dungeon", True, WHITE)
    title_rect = title.get_rect(center=(500, 100))
    screen.blit(title, title_rect)

    dungeon_text = text_font.render(f"Entering: {game.selected_dungeon}", True, GOLD)
    dungeon_rect = dungeon_text.get_rect(center=(500, 300))
    screen.blit(dungeon_text, dungeon_rect)

    instruction_text = text_font.render(
      "Dungeon progression coming soon...", True, GRAY
    )
    instruction_rect = instruction_text.get_rect(center=(500, 500))
    screen.blit(instruction_text, instruction_rect)
