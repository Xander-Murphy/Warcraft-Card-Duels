import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GRAY
from .base import Screen

class EncounterScreen(Screen):
  def handle_input(self, event, game):
    if event.key == pygame.K_RETURN:
      game.state = GameState.COMBAT

    elif event.key == pygame.K_ESCAPE:
      game.state = GameState.DUNGEON

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 64)
    enemy_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 28)

    title = title_font.render(
      "Enemy Encounter", True, WHITE
    )
    title_rect = title.get_rect(center=(500, 80))
    screen.blit(title, title_rect)

    dungeon_text = info_font.render(
      game.selected_dungeon, True, GOLD
    )
    dungeon_rect = dungeon_text.get_rect(center=(500, 140))
    screen.blit(dungeon_text, dungeon_rect)

    for index, enemy in enumerate(game.current_enemies):
      enemy_text = enemy_font.render(
        enemy.name, True, WHITE
      )
      enemy_rect = enemy_text.get_rect(
        center=(500, 250 + index * 60)
      )
      screen.blit(enemy_text, enemy_rect)

      instruction_text = info_font.render(
        "Enter: Begin Combat | Escape: Back", True, GRAY
      )
      instruction_rect = instruction_text.get_rect(center=(500, 620))
      screen.blit(instruction_text, instruction_rect)