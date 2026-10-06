import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GREEN, GRAY
from .base import Screen


class TeamSelectionScreen(Screen):
  def __init__(self):
    self.hero_selection = 0

  def handle_input(self, event, game):
    match event.key:
      case pygame.K_UP | pygame.K_w:
        self.hero_selection -= 1

      case pygame.K_DOWN | pygame.K_s:
        self.hero_selection += 1

      case pygame.K_SPACE:
        self._toggle_hero(game)

      case pygame.K_RETURN:
        if len(game.selected_heroes) == 3:
          game.state = GameState.DUNGEON_SELECTION

      case pygame.K_ESCAPE:
        game.state = GameState.MAIN_MENU
        game.selected_heroes.clear()

    self.hero_selection %= len(game.available_heroes)

  def _toggle_hero(self, game):
    hero = game.available_heroes[self.hero_selection]

    if hero in game.selected_heroes:
      game.selected_heroes.remove(hero)
    elif len(game.selected_heroes) < 3:
      game.selected_heroes.append(hero)

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 64)
    hero_font = pygame.font.Font(None, 36)

    title = title_font.render("Select Your Team", True, WHITE)
    title_rect = title.get_rect(center=(500, 80))
    screen.blit(title, title_rect)

    for index, hero in enumerate(game.available_heroes):
      if index == self.hero_selection:
        hero_color = GOLD
      elif hero in game.selected_heroes:
        hero_color = GREEN
      else:
        hero_color = WHITE

      hero_text = hero_font.render(f"{index + 1}. {hero.name} - {hero.specialization} {hero.character_class}", True, hero_color)
      hero_rect = hero_text.get_rect(center=(500, 180 + index * 60))
      screen.blit(hero_text, hero_rect)

    team_text = hero_font.render(
      f"Your Team: {len(game.selected_heroes)} / 3", True, WHITE
    )
    team_rect = team_text.get_rect(center=(500, 550))
    screen.blit(team_text, team_rect)

    instruction_text = hero_font.render(
      "Arrow Keys or WASD: Move | Space: Select | Enter: Confirm", True, GRAY
    )
    instruction_rect = instruction_text.get_rect(center=(500, 630))
    screen.blit(instruction_text, instruction_rect)