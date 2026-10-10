from abc import ABC, abstractmethod

from targeting import resolver_for


class SelectionState(ABC):
  """One step of choosing a hero's action (State pattern).

  The controller hands every input to its current state, so each step only
  knows its own rules and which step comes next.
  """

  hint = ""  # instruction text for the view to show

  def __init__(self, controller):
    self.controller = controller

  @abstractmethod
  def move(self, step):
    """Move the cursor: -1 for left, +1 for right."""

  @abstractmethod
  def confirm(self):
    """Accept the highlighted choice."""

  @abstractmethod
  def cancel(self):
    """Back out of this step."""


class HeroSelection(SelectionState):
  hint = "Left/Right: Select Hero | Space: Abilities | Enter: End Round"

  def move(self, step):
    self.controller.move_hero(step)

  def confirm(self):
    self.controller.ability_index = 0
    self.controller.state = AbilitySelection(self.controller)

  def cancel(self):
    pass


class AbilitySelection(SelectionState):
  hint = "Left/Right: Select Ability | Space: Choose | Esc: Back"

  def move(self, step):
    self.controller.move_ability(step)

  def confirm(self):
    self.controller.choose_ability()

  def cancel(self):
    self.controller.state = HeroSelection(self.controller)


class TargetSelection(SelectionState):
  hint = "Left/Right: Select Target | Space: Confirm | Esc: Back"

  def move(self, step):
    self.controller.move_target(step)

  def confirm(self):
    self.controller.confirm_target()

  def cancel(self):
    self.controller.state = AbilitySelection(self.controller)


class FightOver(SelectionState):
  hint = "Enter: Continue"

  def move(self, step):
    pass

  def confirm(self):
    pass

  def cancel(self):
    pass


class CombatController:
  """Turns player input into Combat calls and tells the view what to show.

  Holds the cursor positions and the current selection step, but none of
  the combat rules (those live in Combat). Knows nothing about pygame.
  """

  def __init__(self, combat):
    self.combat = combat
    self.hero_index = 0
    self.ability_index = 0
    self.target_index = 0
    self.log = []  # EffectResults from the last resolved round
    self._state: SelectionState = HeroSelection(self)

    self._select_living_hero()
    # Enemies choose first so the player can see what they intend to do
    self.combat.plan_enemy_actions()

  # --- What the view needs ------------------------------------------------

  @property
  def state(self) -> SelectionState:
    """The current selection step: always FightOver once the fight has ended."""
    if self.is_over and not isinstance(self._state, FightOver):
      self._state = FightOver(self)

    return self._state

  @state.setter
  def state(self, new_state: SelectionState):
    self._state = new_state

  @property
  def is_over(self):
    return self.combat.is_over()

  @property
  def heroes_won(self):
    return self.combat.heroes_won()

  @property
  def can_resolve(self):
    return self.combat.is_ready_to_resolve()

  @property
  def selected_hero(self):
    return self.combat.heroes[self.hero_index]

  @property
  def selectable_abilities(self):
    """The selected hero's abilities, with the basic attack as the last entry."""
    hero = self.selected_hero
    return hero.abilities + [hero.basic_attack]

  @property
  def selected_ability(self):
    return self.selectable_abilities[self.ability_index]

  def is_usable(self, ability):
    return self.selected_hero.can_use(ability)

  def target_candidates(self):
    return resolver_for(self.selected_ability.target_type).candidates(
      self.selected_hero, self.combat.battlefield
    )

  def highlighted_target(self):
    """The character under the target cursor, or None outside target selection."""
    if not isinstance(self.state, TargetSelection):
      return None

    candidates = self.target_candidates()

    if not candidates:
      return None

    return candidates[self.target_index % len(candidates)]

  def describe_action(self, action):
    if action is None:
      return ""

    targets = action.targets
    names = targets[0].name if len(targets) == 1 else f"{len(targets)} targets"
    return f"{action.ability.name} -> {names}"

  def queued_text(self, hero):
    return self.describe_action(self.combat.action_for(hero))

  def intent_text(self, enemy):
    return self.describe_action(self.combat.action_for(enemy))

  # --- Input (delegated to the current state) -----------------------------

  def move(self, step):
    self.state.move(step)

  def confirm(self):
    self.state.confirm()

  def cancel(self):
    self.state.cancel()

  def resolve_round(self):
    """Run the round if every living hero has an action. Returns True if it ran."""
    if self.is_over or not self.can_resolve:
      return False

    self.log = self.combat.resolve_round()

    if not self.is_over:
      self.combat.plan_enemy_actions()
      self.state = HeroSelection(self)
      self._select_living_hero()

    return True

  # --- Used by the selection states ---------------------------------------

  def move_hero(self, step):
    heroes = self.combat.heroes

    for _ in range(len(heroes)):
      self.hero_index = (self.hero_index + step) % len(heroes)

      if heroes[self.hero_index].is_alive():
        return

  def move_ability(self, step):
    self.ability_index = (self.ability_index + step) % len(
      self.selectable_abilities
    )

  def move_target(self, step):
    candidates = self.target_candidates()

    if candidates:
      self.target_index = (self.target_index + step) % len(candidates)

  def choose_ability(self):
    hero, ability = self.selected_hero, self.selected_ability

    if not hero.can_use(ability):
      return

    resolver = resolver_for(ability.target_type)

    if resolver.requires_choice:
      # The player picks the target, if there is anyone to pick
      if self.target_candidates():
        self.target_index = 0
        self.state = TargetSelection(self)
    else:
      # Self / all-allies / all-enemies need no choice, so queue straight away
      self._queue(resolver.resolve(hero, self.combat.battlefield))

  def confirm_target(self):
    resolver = resolver_for(self.selected_ability.target_type)

    self._queue(resolver.resolve(
      self.selected_hero, self.combat.battlefield, self.target_index
    ))

  # --- Internals ----------------------------------------------------------

  def _queue(self, targets):
    # replace_action swaps out a hero's earlier choice, so players can re-choose
    action = self.combat.replace_action(
      self.selected_hero, self.selected_ability, targets
    )

    if action is not None:
      self.state = HeroSelection(self)

  def _select_living_hero(self):
    heroes = self.combat.heroes

    if not heroes[self.hero_index].is_alive():
      self.move_hero(1)
