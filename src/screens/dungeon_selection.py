import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GREEN, GRAY
from .base import Screen


class DungeonSelectionScreen(Screen):
  def __init__(self):
    self.dungeon_selection = 0

  def handle_input(self, event, game):
    match event.key:
      case pygame.K_UP | pygame.K_w:
        self.dungeon_selection -= 1

      case pygame.K_DOWN | pygame.K_s:
        self.dungeon_selection += 1

      case pygame.K_SPACE:
        game.selected_dungeon = game.available_dungeons[self.dungeon_selection]

      case pygame.K_RETURN:
        if game.selected_dungeon is not None:
          game.state = GameState.DUNGEON

      case pygame.K_ESCAPE:
        game.state = GameState.TEAM_SELECTION

    self.dungeon_selection %= len(game.available_dungeons)

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 64)
    dungeon_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 28)

    title = title_font.render("Select Your Dungeon", True, WHITE)
    title_rect = title.get_rect(center=(500, 80))
    screen.blit(title, title_rect)

    for index, dungeon in enumerate(game.available_dungeons):
      if index == self.dungeon_selection:
        dungeon_color = GOLD
      elif dungeon == game.selected_dungeon:
        dungeon_color = GREEN
      else:
        dungeon_color = WHITE

      dungeon_text = dungeon_font.render(
        f"{index + 1}. {dungeon}", True, dungeon_color
      )
      dungeon_rect = dungeon_text.get_rect(center=(500, 220 + index * 80))
      screen.blit(dungeon_text, dungeon_rect)

    if game.selected_dungeon is None:
      selected_text = "Selected Dungeon: None"
    else:
      selected_text = f"Selected Dungeon: {game.selected_dungeon}"

    selected_surface = info_font.render(selected_text, True, WHITE)
    selected_rect = selected_surface.get_rect(center=(500, 500))
    screen.blit(selected_surface, selected_rect)

    instruction_text = info_font.render(
      "Arrow Keys or W and S: Move | Space: Select | Enter: Confirm", True, GRAY
    )
    instruction_rect = instruction_text.get_rect(center=(500, 620))
    screen.blit(instruction_text, instruction_rect)