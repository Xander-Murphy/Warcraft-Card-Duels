from actions import Action
from combat_round import CombatRound
from targeting import Battlefield


class Combat:
  """One fight between the party and a group of enemies.

  Runs in rounds. During a round each living character may queue one action:
  the player queues the heroes' actions, and plan_enemy_actions() asks each
  enemy's behavior for theirs. resolve_round() then performs the queued
  actions fastest-first and does the round-end upkeep (poison, effect
  durations, cooldowns).

  Cooldowns tick at the end of every round, including the round an ability
  was used in. A cooldown of 1 can therefore be used every round, 2 every
  other round, and so on.

  When two actions have the same priority the heroes' action goes first, and
  otherwise the one queued first. (Enemies may queue before the player picks
  their actions, so this is spelled out rather than left to queue order.)

  This class knows nothing about pygame, so it can be tested without a display.
  """

  def __init__(self, heroes, enemies):
    self.battlefield = Battlefield(heroes, enemies)
    self.combat_round = CombatRound()
    self.round_number = 1

  # --- Who is in the fight ------------------------------------------------

  @property
  def heroes(self):
    return self.battlefield.heroes

  @property
  def enemies(self):
    return self.battlefield.enemies

  def living_heroes(self):
    return [hero for hero in self.heroes if hero.is_alive()]

  def living_enemies(self):
    return [enemy for enemy in self.enemies if enemy.is_alive()]

  def is_over(self):
    """True once either side has no one left standing."""
    return not self.living_heroes() or not self.living_enemies()

  def heroes_won(self):
    """True if the fight is over and at least one hero is still standing."""
    return self.is_over() and bool(self.living_heroes())

  # --- Planning the round -------------------------------------------------

  def action_for(self, actor):
    """The action `actor` has queued this round, or None."""
    for action in self.combat_round.action_queue.actions:
      if action.actor is actor:
        return action

    return None

  def heroes_awaiting_orders(self):
    return [
      hero for hero in self.living_heroes()
      if self.action_for(hero) is None
    ]

  def is_ready_to_resolve(self):
    """True once every living hero has queued an action."""
    return not self.is_over() and not self.heroes_awaiting_orders()

  def can_queue(self, actor, ability):
    return self._can_act(actor, ability) and self.action_for(actor) is None

  def _can_act(self, actor, ability):
    # can_use covers ownership, cooldown, and the basic-attack fallback rule
    return (
      not self.is_over()
      and self._is_in_fight(actor)
      and actor.is_alive()
      and actor.can_use(ability)
    )

  def queue_action(self, actor, ability, targets):
    """Queue an action for this round.

    Returns the Action, or None if it isn't allowed (actor dead or already
    acting, ability on cooldown or not theirs, or no living target).
    """
    return self.add_action(Action(actor, ability, targets))

  def add_action(self, action):
    """Queue a ready-made Action, applying the same rules as queue_action."""
    if not self.can_queue(action.actor, action.ability):
      return None

    if not action.has_living_target():
      return None

    self.combat_round.add_action(action)
    return action

  def cancel_action(self, actor):
    """Remove `actor`'s queued action. Returns it, or None if they had none."""
    action = self.action_for(actor)

    if action is not None:
      self.combat_round.action_queue.remove_action(action)

    return action

  def replace_action(self, actor, ability, targets):
    """Queue an action, swapping out any the actor already has.

    If the new action isn't allowed, nothing changes: the old action stays.
    Returns the new Action, or None.
    """
    action = Action(actor, ability, targets)

    if not self._can_act(actor, ability) or not action.has_living_target():
      return None

    self.cancel_action(actor)
    return self.add_action(action)

  def plan_enemy_actions(self):
    """Let every living enemy that has no orders yet choose its action.

    Returns the actions that were queued.
    """
    planned = []

    for enemy in self.living_enemies():
      if self.action_for(enemy) is not None:
        continue

      choice = enemy.behavior.choose_action(enemy, self.battlefield)
      action = self.add_action(choice) if choice is not None else None

      if action is not None:
        planned.append(action)

    return planned

  def _is_hero(self, actor):
    return any(actor is hero for hero in self.heroes)

  def _is_in_fight(self, actor):
    return any(actor is member for member in self.heroes + self.enemies)

  # --- Resolving the round ------------------------------------------------

  def resolve_round(self):
    """Perform the queued actions, then end the round.

    Returns every EffectResult that happened, in order, for the combat log.
    Does nothing once the fight is over.
    """
    results = []

    if self.is_over():
      return results

    queue = self.combat_round.action_queue

    # Heroes first, so they win ties however the queue was filled. The sort
    # is stable, so queue order still decides ties within a side.
    queue.actions.sort(key=lambda action: not self._is_hero(action.actor))
    self.combat_round.prepare()

    while (action := queue.get_next_action()) is not None:
      if self.is_over():
        break

      # Skips actors who died earlier this round, and attacks whose
      # targets are already dead (without spending the cooldown).
      if action.can_execute():
        results.extend(action.execute())

    self.combat_round = CombatRound()

    if not self.is_over():
      results.extend(self._end_round())
      self.round_number += 1

    return results

  def _end_round(self):
    results = []

    for character in self.heroes + self.enemies:
      if character.is_alive():
        results.extend(character.end_round())

    return results
