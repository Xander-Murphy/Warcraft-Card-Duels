import pygame

from states import GameState

class Game:
  def __init__(self, screen):
    self.screen = screen
    self.running = True
    self.state = GameState.MAIN_MENU
    self.menu_selection = 0

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT: # if the application is closed the process stops running
        self.running = False

      elif event.type == pygame.KEYDOWN: 
        if self.state == GameState.MAIN_MENU:
          if event.key in (pygame.K_UP, pygame.K_w): # pressing the ↑ or W moves the selection up
            self.menu_selection -= 1

          elif event.key in (pygame.K_DOWN, pygame.K_s): # pressing the ↓ or S moves the selection down
            self.menu_selection += 1

          elif event.key == pygame.K_RETURN:          # if the user presses enter on the 
            if self.menu_selection == 0:              # start game button they will enter 
              self.state = GameState.TEAM_SELECTION   # team selection.
                                                      
            elif self.menu_selection == 1:            # if user selects quit the game
              self.running = False                    # stops running and closes

          self.menu_selection %= 2 # keeps selection between 0 and 1

          


  def update(self):
    pass

  def draw(self):
    self.screen.fill((30, 30, 30))

    title_font = pygame.font.Font(None, 72)
    button_font = pygame.font.Font(None, 42)

    title = title_font.render("Warcraft Card Duels", True, (255, 255, 255))

    start_color = (255, 215, 0) if self.menu_selection == 0 else (255, 255, 255) # These are the colors of the menu options
    quit_color = (255, 215, 0) if self.menu_selection == 1 else (255, 255, 255)  # menu options change color based off the menu variable


    start_text = button_font.render("Start Game", True, start_color)
    quit_text = button_font.render("Quit Game", True, quit_color)

    title_rect = title.get_rect(center=(500, 150))
    start_rect = start_text.get_rect(center=(500, 350))
    quit_rect = quit_text.get_rect(center=(500, 450))

    self.screen.blit(title, title_rect)
    self.screen.blit(start_text, start_rect)
    self.screen.blit(quit_text, quit_rect)

  def run(self):
    clock = pygame.time.Clock()

    while self.running:
      self.handle_events()
      self.update()
      self.draw()

      pygame.display.flip()
      clock.tick(60)