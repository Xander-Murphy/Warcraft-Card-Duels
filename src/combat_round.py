from action_queue import ActionQueue

class CombatRound:
  def __init__(self):
    self.action_queue = ActionQueue()

  def add_action(self, action):
    self.action_queue.add_action(action)

  def prepare(self):
    self.action_queue.sort_actions()