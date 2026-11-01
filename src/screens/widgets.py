"""Small drawing helpers shared by several screens."""
from lib.colors import WHITE, GRAY


def draw_text(screen, font, text, color, center):
  rendered = font.render(text, True, color)
  screen.blit(rendered, rendered.get_rect(center=center))


def status_line(character):
  """'Koryne - HP 60/75', or 'Koryne - Defeated' once they are down."""
  if not character.is_alive():
    return f"{character.name} - Defeated"

  return f"{character.name} - HP {character.health}/{character.max_health}"


def draw_status_lines(screen, font, characters, top, spacing, x=500):
  """One centred status line per character, defeated ones greyed out."""
  for index, character in enumerate(characters):
    color = WHITE if character.is_alive() else GRAY
    draw_text(
      screen, font, status_line(character), color, (x, top + index * spacing)
    )
