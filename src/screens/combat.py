import pygame

from states import GameState
from lib.colors import WHITE, GOLD, GREEN, GRAY
from actions import Action
from combat_round import CombatRound
from targeting import Battlefield, resolver_for
from .base import Screen

class CombatScreen(Screen):
  def __init__(self):
    self.hero_selection = 0
    self.ability_selection = 0
    self.target_selection = 0

    self.selection_mode = "hero"

    self.combat_round = CombatRound()

  def _navigate_selection(self, event, selection, item_count):
    match event.key:
      case pygame.K_LEFT | pygame.K_a:
        selection -= 1

      case pygame.K_RIGHT | pygame.K_d:
        selection += 1

    return selection % item_count
  
  def _has_queued_action(self, hero):
    return any(
      action.actor is hero
      for action in self.combat_round.action_queue.actions
    )
  
  def _get_positions(self, count, center_x=500, spacing= 250):
    if count == 0:
      return []

    total_width = (count - 1) * spacing
    start_x = center_x - total_width / 2

    return [
      (start_x + index * spacing)
      for index in range(count)
    ]

  def _selected_hero(self, game):
    return game.party[self.hero_selection]

  def _selected_ability(self, game):
    return self._selected_hero(game).abilities[self.ability_selection]

  def _resolver(self, game):
    return resolver_for(self._selected_ability(game).target_type)

  def _battlefield(self, game):
    return Battlefield(game.party, game.current_enemies)

  def _target_candidates(self, game):
    return self._resolver(game).candidates(
      self._selected_hero(game),
      self._battlefield(game)
    )

  def _highlighted_target(self, game):
    """The character under the target cursor, or None outside target mode."""
    if self.selection_mode != "target" or not game.party:
      return None

    candidates = self._target_candidates(game)

    if not candidates:
      return None

    return candidates[self.target_selection % len(candidates)]

  def _confirm_ability(self, game):
    resolver = self._resolver(game)

    if resolver.requires_choice:
      # Player picks the target (if there is anyone to pick)
      if self._target_candidates(game):
        self.selection_mode = "target"
        self.target_selection = 0
    else:
      # Self / all-allies / all-enemies need no choice, so queue straight away
      self._queue_action(game, resolver.resolve(
        self._selected_hero(game),
        self._battlefield(game)
      ))

  def _queue_action(self, game, targets):
    if not targets:
      return

    self.combat_round.add_action(Action(
      self._selected_hero(game),
      self._selected_ability(game),
      targets
    ))
    self.selection_mode = "hero"

  def handle_input(self, event, game):
    if not game.party:
      return
    # Controls hero selection
    if self.selection_mode == "hero":
      match event.key:
        case pygame.K_LEFT | pygame.K_a | pygame.K_RIGHT | pygame.K_d:
          self.hero_selection = self._navigate_selection(
            event,
            self.hero_selection,
            len(game.party)
          )
        case pygame.K_SPACE:
            self.selection_mode = "ability"
            self.ability_selection = 0
            
    # Controls ability selection for selected heroes
    elif self.selection_mode == "ability":
      selected_hero = game.party[self.hero_selection]

      match event.key:
        case pygame.K_LEFT | pygame.K_a | pygame.K_RIGHT | pygame.K_d:
          self.ability_selection = self._navigate_selection(
            event,
            self.ability_selection,
            len(selected_hero.abilities)
          )
        case pygame.K_SPACE:
          self._confirm_ability(game)
        case pygame.K_ESCAPE:
          self.selection_mode = "hero"

    elif self.selection_mode == "target":
      candidates = self._target_candidates(game)

      if not candidates:
        self.selection_mode = "ability"
        return

      match event.key:
        case pygame.K_LEFT | pygame.K_a | pygame.K_RIGHT | pygame.K_d:
          self.target_selection = self._navigate_selection(
            event,
            self.target_selection,
            len(candidates)
          )
        case pygame.K_SPACE:
          self._queue_action(game, self._resolver(game).resolve(
            self._selected_hero(game),
            self._battlefield(game),
            self.target_selection
          ))
        case pygame.K_ESCAPE:
          self.selection_mode = "ability"

  def draw(self, screen, game):
    title_font = pygame.font.Font(None, 48)
    character_font = pygame.font.Font(None, 32)
    info_font = pygame.font.Font(None, 24)

    # Title
    title = title_font.render(
      f"{game.selected_dungeon} - Combat",
      True,
      WHITE
    )
    title_rect = title.get_rect(center=(500, 50))
    screen.blit(title, title_rect)

    target = self._highlighted_target(game)

    # Enemies
    enemy_positions = self._get_positions(len(game.current_enemies))

    for index, enemy in enumerate(game.current_enemies):
      if enemy is target:
          enemy_color = GOLD
      else:
          enemy_color = WHITE

      enemy_text = character_font.render(
          enemy.name,
          True,
          enemy_color
      )
      enemy_rect = enemy_text.get_rect(
        center=(enemy_positions[index], 180)
      )
      screen.blit(enemy_text, enemy_rect)

    # Heroes
    for index, hero in enumerate(game.party):
      if target is not None:
        hero_color = GOLD if hero is target else WHITE
      elif index == self.hero_selection:
        hero_color = GOLD
      else:
        hero_color = WHITE

      hero_text = character_font.render(
        hero.name,
        True,
        hero_color
      )

      hero_rect = hero_text.get_rect(
        center=(250 + index * 250, 450)
      )

      screen.blit(hero_text, hero_rect)

      # Draw abilities for selected hero
      if game.party:
        selected_hero = game.party[self.hero_selection]

        ability_positions = self._get_positions(
          len(selected_hero.abilities)
        )

        for index, abilty in enumerate(selected_hero.abilities):
          if (
            self.selection_mode == "ability" and index == self.ability_selection
          ):
            ability_color = GOLD
          else:
            ability_color = WHITE

          ability_text = info_font.render(
            abilty.name,
            True,
            ability_color
          )

          abilty_rect = ability_text.get_rect(
            center=(ability_positions[index], 520)
          )
          screen.blit(ability_text,abilty_rect)

      # Draw ability description
      if self.selection_mode == "ability":
        selected_hero = game.party[self.hero_selection]
        selected_ability = selected_hero.abilities[self.ability_selection]

        description_text = info_font.render(
          selected_ability.description,
          True,
          WHITE
        )

        description_rect = description_text.get_rect(
          center=(500, 570)
        )
        screen.blit(description_text, description_rect)

      if self.selection_mode == "target":
        target_text = info_font.render(
          "Select a target",
          True,
          GOLD
        )

        target_rect = target_text.get_rect(
          center=(500, 600)
        )
        screen.blit(target_text, target_rect)

      # Instructions
      instruction_text = info_font.render(
        "Arorw Keys / WASD: Select Hero | Space: Abilities",
        True,
        GRAY
      )
      instruction_rect = instruction_text.get_rect(
        center=(500, 670)
      )

      screen.blit(instruction_text, instruction_rect)