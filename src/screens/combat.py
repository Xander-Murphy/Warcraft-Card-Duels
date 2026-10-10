import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GREEN, GRAY, RED
from combat_controller import (
  AbilitySelection, CombatController, HeroSelection, TargetSelection
)
from .base import Screen

LOG_LINES = 6  # how many lines of the last round's results to show


class CombatScreen(Screen):
  """Shows a fight and turns key presses into controller calls.

  All the rules live in Combat and all the cursor logic in CombatController;
  this class only maps keys to the controller and draws what it reports.
  """

  def __init__(self):
    self.controller = None

  def _controller_for(self, game):
    """The controller for the fight in progress (a new one for each new fight)."""
    if game.combat is None:
      self.controller = None
    elif self.controller is None or self.controller.combat is not game.combat:
      self.controller = CombatController(game.combat)

    return self.controller

  def handle_input(self, event, game):
    controller = self._controller_for(game)

    if controller is None:
      return

    match event.key:
      case pygame.K_LEFT | pygame.K_a:
        controller.move(-1)
      case pygame.K_RIGHT | pygame.K_d:
        controller.move(1)
      case pygame.K_SPACE:
        controller.confirm()
      case pygame.K_ESCAPE:
        controller.cancel()
      case pygame.K_RETURN:
        self._handle_enter(controller, game)

  def _handle_enter(self, controller, game):
    if not controller.is_over:
      controller.resolve_round()
      return

    # The fight is over: a win goes back to the dungeon, a loss to the menu
    game.end_combat()
    game.state = (
      GameState.DUNGEON if controller.heroes_won else GameState.MAIN_MENU
    )

  # --- Drawing ------------------------------------------------------------

  def _get_positions(self, count, center_x=500, spacing=250):
    if count == 0:
      return []

    total_width = (count - 1) * spacing
    start_x = center_x - total_width / 2

    return [start_x + index * spacing for index in range(count)]

  def _text(self, screen, font, text, color, center):
    rendered = font.render(text, True, color)
    screen.blit(rendered, rendered.get_rect(center=center))

  def draw(self, screen, game):
    controller = self._controller_for(game)

    if controller is None:
      return

    fonts = {
      "title": pygame.font.Font(None, 48),
      "banner": pygame.font.Font(None, 80),
      "name": pygame.font.Font(None, 32),
      "info": pygame.font.Font(None, 24),
    }

    self._draw_header(screen, fonts, controller, game)
    self._draw_enemies(screen, fonts, controller)
    self._draw_log_and_banner(screen, fonts, controller)
    self._draw_heroes(screen, fonts, controller)
    self._draw_abilities(screen, fonts, controller)
    self._draw_prompts(screen, fonts, controller)

  def _draw_header(self, screen, fonts, controller, game):
    self._text(
      screen, fonts["title"], f"{game.selected_dungeon} - Combat", WHITE, (500, 40)
    )
    self._text(
      screen, fonts["info"], f"Round {controller.combat.round_number}",
      GRAY, (500, 78)
    )

  def _name_color(self, character, highlighted):
    if not character.is_alive():
      return GRAY

    return GOLD if highlighted else WHITE

  def _health_text(self, character):
    if not character.is_alive():
      return "Defeated"

    return f"HP {character.health}/{character.max_health}"

  def _draw_enemies(self, screen, fonts, controller):
    enemies = controller.combat.enemies
    target = controller.highlighted_target()

    for enemy, x in zip(enemies, self._get_positions(len(enemies))):
      self._text(
        screen, fonts["name"], enemy.name,
        self._name_color(enemy, enemy is target), (x, 130)
      )
      self._text(
        screen, fonts["info"], self._health_text(enemy), GRAY, (x, 158)
      )

      # What this enemy plans to do this round
      if enemy.is_alive():
        self._text(
          screen, fonts["info"], controller.intent_text(enemy), RED, (x, 184)
        )

  def _draw_log_and_banner(self, screen, fonts, controller):
    if controller.is_over:
      won = controller.heroes_won
      self._text(
        screen, fonts["banner"], "VICTORY" if won else "DEFEAT",
        GREEN if won else RED, (500, 250)
      )

    for index, result in enumerate(controller.log[-LOG_LINES:]):
      self._text(
        screen, fonts["info"], result.description, GRAY, (500, 310 + index * 24)
      )

  def _draw_heroes(self, screen, fonts, controller):
    heroes = controller.combat.heroes
    target = controller.highlighted_target()

    for index, (hero, x) in enumerate(
      zip(heroes, self._get_positions(len(heroes)))
    ):
      if target is not None:
        highlighted = hero is target
      else:
        highlighted = index == controller.hero_index and not controller.is_over

      self._text(
        screen, fonts["name"], hero.name,
        self._name_color(hero, highlighted), (x, 470)
      )
      self._text(
        screen, fonts["info"], self._health_text(hero), GRAY, (x, 498)
      )

      # The action this hero has chosen for this round
      if hero.is_alive():
        self._text(
          screen, fonts["info"], controller.queued_text(hero), GREEN, (x, 522)
        )

  def _ability_label(self, controller, ability):
    if controller.is_usable(ability):
      return ability.name

    return f"{ability.name} (CD {ability.current_cooldown})"

  def _draw_abilities(self, screen, fonts, controller):
    if controller.is_over:
      return

    abilities = controller.selectable_abilities
    choosing = isinstance(controller.state, (AbilitySelection, TargetSelection))

    for index, (ability, x) in enumerate(
      zip(abilities, self._get_positions(len(abilities)))
    ):
      selected = choosing and index == controller.ability_index

      if selected:
        color = GOLD
      elif controller.is_usable(ability):
        color = WHITE
      else:
        color = GRAY

      self._text(
        screen, fonts["info"], self._ability_label(controller, ability),
        color, (x, 565)
      )

    if isinstance(controller.state, AbilitySelection):
      self._text(
        screen, fonts["info"], self._ability_description(controller),
        WHITE, (500, 600)
      )

  def _ability_description(self, controller):
    ability = controller.selected_ability

    if controller.is_usable(ability):
      return ability.description

    return f"On cooldown: {ability.current_cooldown} more round(s)"

  def _draw_prompts(self, screen, fonts, controller):
    state = controller.state

    if isinstance(state, TargetSelection):
      self._text(screen, fonts["info"], "Select a target", GOLD, (500, 635))
    elif isinstance(state, HeroSelection) and not controller.can_resolve:
      self._text(
        screen, fonts["info"], "Choose an action for every hero",
        GRAY, (500, 635)
      )
    elif isinstance(state, HeroSelection):
      self._text(
        screen, fonts["info"], "Everyone is ready: press Enter", GOLD, (500, 635)
      )

    self._text(screen, fonts["info"], state.hint, GRAY, (500, 675))