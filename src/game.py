import pygame

from states import GameState

class Game:
  def __init__(self, screen):
    self.screen = screen
    self.running = True
    self.state = GameState.MAIN_MENU
    self.menu_selection = 0

    self.available_heroes = [ # stores the heroes available to pick
      "Warrior",
      "Mage",
      "Priest",
      "Hunter",
      "Rogue"
    ]

    self.selected_heroes = [] # stores heroes the player selects for their team
    self.hero_selection = 0 # starts the selected hero list at the first entry

    self.available_dungeons = [
      "Ragefire Chasm",
      "Wailing Caverns",
      "The Deadmines",
    ]

    self.dungeon_selection = 0
    self.selected_dungeon = None

  def handle_events(self): # This function handles events checks the current game state and uses specific screen functions depending on the current state
    for event in pygame.event.get():
      if event.type == pygame.QUIT: 
        self.running = False

      elif event.type == pygame.KEYDOWN: 

        if self.state == GameState.MAIN_MENU: 
          self.handle_main_menu_input(event)  

        elif self.state == GameState.TEAM_SELECTION: 
          self.handle_team_selection_input(event)    

        elif self.state == GameState.DUNGEON_SELECTION:
          self.handle_dungeon_selection_input(event)

        elif self.state == GameState.ENCOUNTER:
          self.handle_encounter_input(event)

  def handle_main_menu_input(self, event): # This function handles keyboard input when the game state is set to MAIN_MENU
    if event.key in (pygame.K_UP, pygame.K_w): # pressing the ↑ or W moves the selection up
      self.menu_selection -= 1

    elif event.key in (pygame.K_DOWN, pygame.K_s): # pressing the ↓ or S moves the selection down
      self.menu_selection += 1

    elif event.key == pygame.K_RETURN:          
      if self.menu_selection == 0:               
        self.state = GameState.TEAM_SELECTION   
                                                
      elif self.menu_selection == 1:            
        self.running = False                    

    self.menu_selection %= 2 # keeps selection between 0 and 1

  def handle_team_selection_input(self, event): # This function handles keyboard input when the game state is set to TEAM_SELECTION
    if event.key in (pygame.K_UP, pygame.K_w): # pressing the ↑ or W moves the selection up
      self.hero_selection -= 1

    elif event.key in (pygame.K_DOWN, pygame.K_s): # pressing the ↓ or S moves the selection down
      self.hero_selection += 1

    elif event.key == pygame.K_SPACE: # pressing the spacebar selects a hero
      hero = self.available_heroes[self.hero_selection]

      if hero in self.selected_heroes: # if hero is selected already deselect it
        self.selected_heroes.remove(hero)

      elif len(self.selected_heroes) < 3: # if heroes selected is less than 3 add it to the selected list
        self.selected_heroes.append(hero)  

    elif event.key == pygame.K_RETURN: # if ENTER key is pressed and 3 heroes are selected move to encounter state
      if len(self.selected_heroes) == 3:
        self.state = GameState.DUNGEON_SELECTION
    
    elif event.key == pygame.K_ESCAPE: # if ESC is pressed return to main menu and clear hero selection
      self.state = GameState.MAIN_MENU
      self.selected_heroes.clear()

    self.hero_selection %= len(self.available_heroes)

  def handle_dungeon_selection_input(self, event):
    if event.key in (pygame.K_UP, pygame.K_w):
      self.dungeon_selection -= 1

    elif event.key in (pygame.K_DOWN, pygame.K_s):
      self.dungeon_selection += 1

    elif event.key == pygame.K_SPACE:
      self.selected_dungeon = (self.available_dungeons[self.dungeon_selection])

    elif event.key == pygame.K_RETURN:
      if self.selected_dungeon is not None:
        self.state = GameState.DUNGEON

    elif event.key == pygame.K_ESCAPE:
      self.state = GameState.TEAM_SELECTION

    self.dungeon_selection %= len(self.available_dungeons)


  def update(self):
    pass

  def draw(self):
    self.screen.fill((30, 30, 30))

    if self.state == GameState.MAIN_MENU: # if statement checks what game state we are in
      self.draw_main_menu()               # will draw the screen based on state
    elif self.state == GameState.TEAM_SELECTION:
      self.draw_team_selection()
    elif self.state == GameState.DUNGEON_SELECTION:
      self.draw_dungeon_selection()
    elif self.state == GameState.DUNGEON:
      self.draw_dungeon()
    elif self.state == GameState.ENCOUNTER:
      self.draw_encounter()
    elif self.state == GameState.COMBAT:
      self.draw_combat()


  def draw_main_menu(self):
    self.screen.fill((30, 30, 30))

    title_font = pygame.font.Font(None, 72)  # Title font/size
    button_font = pygame.font.Font(None, 42) # Button font/size

    title = title_font.render("Warcraft Card Duels", True, (255, 255, 255)) # Game title Text

    start_color = (255, 215, 0) if self.menu_selection == 0 else (255, 255, 255) # These are the colors of the menu options
    quit_color = (255, 215, 0) if self.menu_selection == 1 else (255, 255, 255)  # menu options change color based off the menu variable


    start_text = button_font.render("Start Game", True, start_color) # Start button text
    quit_text = button_font.render("Quit Game", True, quit_color)    # Quit button text

    title_rect = title.get_rect(center=(500, 150))      # Positing of title, start,
    start_rect = start_text.get_rect(center=(500, 350)) # and quit buttons
    quit_rect = quit_text.get_rect(center=(500, 450)) 

    self.screen.blit(title, title_rect)       # Physically draws
    self.screen.blit(start_text, start_rect)  # the buttons on screen
    self.screen.blit(quit_text, quit_rect)    

  def draw_team_selection(self):
    title_font = pygame.font.Font(None, 64)
    hero_font = pygame.font.Font(None, 36)

    title = title_font.render("Select Your Team", True, (255, 255, 255))

    title_rect = title.get_rect(center=(500, 80))
    self.screen.blit(title, title_rect)

    for index, hero in enumerate(self.available_heroes):
      if index == self.hero_selection:
        hero_color = (255, 215, 0) # yellow while hovered over

      elif hero in self.selected_heroes:
        hero_color = (0, 255, 0) # Green while selected

      else:
        hero_color = (255, 255, 255) # White while available

      hero_text = hero_font.render(f"{index + 1}. {hero}", True, hero_color)

      hero_rect = hero_text.get_rect(center=(500, 180 + index * 60))

      self.screen.blit(hero_text, hero_rect)


    team_text = hero_font.render(
      f"Your Team: {len(self.selected_heroes)} / 3",
      True,
      (255, 255, 255)
    )

    team_rect = team_text.get_rect(center=(500, 550))
    self.screen.blit(team_text, team_rect)

    instruction_text = hero_font.render(
      "Arrow Keys or WASD: Move | Space: Select | Enter: Confirm",
      True,
      (180, 180, 180)
    )

    instruction_rect = instruction_text.get_rect(center=(500, 630))
    self.screen.blit(instruction_text, instruction_rect)

  def draw_dungeon_selection(self):
    title_font = pygame.font.Font(None, 64)
    dungeon_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 28)

    title = title_font.render("Select Your Dungeon", True, (255, 255, 255))

    title_rect = title.get_rect(center=(500, 80))
    self.screen.blit(title, title_rect)

    for index, dungeon in enumerate(self.available_dungeons):
      if index == self.dungeon_selection:
        dungeon_color = (255, 215, 0)

      elif dungeon == self.selected_dungeon:
        dungeon_color = (0, 255, 0)

      else:
        dungeon_color = (255, 255, 255)

      dungeon_text = dungeon_font.render(
        f"{index + 1}. {dungeon}", True, dungeon_color
      )

      dungeon_rect = dungeon_text.get_rect(
        center=(500, 220 + index * 80)
      )

      self.screen.blit(dungeon_text, dungeon_rect)

    if self.selected_dungeon is None:
      selected_text = "Selected Dungeon: None"
    else:
      selected_text = f"Selected Dungeon: {self.selected_dungeon}"

    selected_surface = info_font.render(
      selected_text, True, (255, 255, 255)
    )

    selected_rect = selected_surface.get_rect(center=(500, 500))
    self.screen.blit(selected_surface, selected_rect)

    instruction_text = info_font.render(
      "Arrow Keys or W and S: Move | Space: Select | Enter: Confirm",
      True,
      (180, 180, 180)
    )

    instruction_rect = instruction_text.get_rect(center=(500,620))
    self.screen.blit(instruction_text,instruction_rect)

  def draw_dungeon(self):
    title_font = pygame.font.Font(None, 64)
    text_font = pygame.font.Font(None, 36)

    title = title_font.render(
      "Dugeon",
      True,
      (255, 255, 255)
    )

    title_rect = title.get_rect(center=(500, 100))
    self.screen.blit(title, title_rect)

    dungeon_text = text_font.render(
      f"Entering: {self.selected_dungeon}",
      True,
      (255, 215, 0)
    )

    instruction_text = text_font.render(
      "Dungeon progression coming soon...",
      True,
      (180, 180, 180)
    )

    instruction_rect = instruction_text.get_rect(center=(500, 500))
    self.screen.blit(instruction_text, instruction_rect)

    dungeon_rect = dungeon_text.get_rect(center=(500, 300))
    self.screen.blit(dungeon_text, dungeon_rect)


  def run(self):
    clock = pygame.time.Clock()

    while self.running:
      self.handle_events()
      self.update()
      self.draw()

      pygame.display.flip()
      clock.tick(60)