class Screen:
  """Base interface every screen implements.

  Game just calls handle_input()/draw() on whichever screen matches
  the current GameState — it doesn't need to know what's inside.
  """

  def handle_input(self, event, game):
    raise NotImplementedError

  def draw(self, screen, game):
    raise NotImplementedError
