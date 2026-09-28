import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GRAY
from .base import Screen


class DungeonScreen(Screen):
  def handle_input(self, event, game):
    if event.key == pygame.K_RETURN:
      game.state = GameState.ENCOUNTER

    elif event.key == pygame.K_ESCAPE:
      game.state = GameState.DUNGEON_SELECTION

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 64)
    text_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 28)

    title = title_font.render(game.selected_dungeon, True, WHITE)
    title_rect = title.get_rect(center=(500, 80))
    screen.blit(title, title_rect)

    progress_text = text_font.render(
      f"Encounter {game.current_encounter + 1 } / {game.total_encounters}", True, GOLD
    )
    progress_rect = progress_text.get_rect(center=(500, 180))
    screen.blit(progress_text, progress_rect)

    encounter_text = text_font.render(
      "A group of enemies awaits...", True, WHITE
    )
    encounter_rect = encounter_text.get_rect(center=(500, 300))
    screen.blit(encounter_text, encounter_rect)

    boss_text = info_font.render(
      "Boss awaits ad the end of the dungeon", True, GRAY
    )
    boss_rect = boss_text.get_rect(center=(500, 400))
    screen.blit(boss_text, boss_rect)

    instruction_text = info_font.render(
      "Enter: Begin Encounter | Escape: Back", True, GRAY)
    instruction_rect = instruction_text.get_rect(center=(500, 620))
    screen.blit(instruction_text, instruction_rect)
