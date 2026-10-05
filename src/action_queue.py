class ActionQueue:
  def __init__(self):
    self.actions = []

  def add_action(self, action):
    self.actions.append(action)

  def sort_actions(self):
    self.actions.sort(
      key=lambda action: action.priority,
      reverse=True
    )

  def get_next_action(self):
    if self.actions:
      return self.actions.pop(0)

    return None