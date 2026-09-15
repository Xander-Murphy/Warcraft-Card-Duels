import pygame

from game import Game

WIDTH = 1000
HEIGHT = 700

def main():
  pygame.init()

  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Warcraft Card Duels")

  game = Game(screen)
  game.run()

  pygame.quit()

if __name__ == "__main__":
  main()