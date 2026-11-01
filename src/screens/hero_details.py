from dataclasses import dataclass

import pygame

from lib.colors import WHITE, GOLD, GRAY


@dataclass(frozen=True)
class DetailLine:
  text: str
  style: str  # "heading", "stats", "ability" or "description"


class HeroDetails:
  """Describes one hero (stats, resistances, abilities) and draws it as a panel.

  Building the text is separate from drawing it, so what the panel says can
  be tested without pygame, and another screen can reuse the panel as is.
  """

  STYLES = {
    # style: (font size, color, gap below the line)
    "heading": (40, GOLD, 34),
    "stats": (26, WHITE, 26),
    "ability": (26, WHITE, 20),
    "description": (22, GRAY, 28),
  }

  def lines(self, hero):
    lines = [
      DetailLine(hero.name, "heading"),
      DetailLine(f"{hero.specialization} {hero.character_class}", "description"),
      DetailLine(
        f"HP {hero.max_health}   Attack {hero.attack}   "
        f"Defense {hero.defense}   Speed {hero.speed}",
        "stats",
      ),
    ]

    resistances = self._resistance_text(hero)
    if resistances:
      lines.append(DetailLine(resistances, "description"))

    for ability in hero.abilities:
      lines.append(DetailLine(self._ability_text(ability), "ability"))
      lines.append(DetailLine(ability.description, "description"))

    return lines

  def _resistance_text(self, hero):
    parts = [
      f"{school.value} {amount:+d}%"
      for school, amount in hero.resistances.items()
      if amount
    ]
    return "Resistances: " + ", ".join(parts) if parts else ""

  def _ability_text(self, ability):
    parts = [ability.name, ability.target_type.value]

    if ability.deals_damage():
      parts.append(f"Power {ability.power}")

    parts.append(f"Cooldown {ability.cooldown}")
    return " - ".join(parts)

  def draw(self, screen, hero, topleft):
    x, y = topleft

    for line in self.lines(hero):
      size, color, gap = self.STYLES[line.style]
      rendered = pygame.font.Font(None, size).render(line.text, True, color)
      screen.blit(rendered, (x, y))
      y += gap
