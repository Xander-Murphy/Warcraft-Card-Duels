import pygame

from states import GameState

class Game:
  def __init__(self, screen):
    self.screen = screen
    self.running = True
    self.state = GameState.MAIN_MENU

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False

  def update(self):
    pass

  def draw(self):
    self.screen.fill((30, 30, 30))

  def run(self):
    clock = pygame.time.Clock()

    while self.running:
      self.handle_events()
      self.update()
      self.draw()

      pygame.display.flip()
      clock.tick(60)