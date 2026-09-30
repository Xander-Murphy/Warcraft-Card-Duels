from characters import Character

class Hero(Character):
  def __init__(
      self,
      name,
      character_class,
      specialization,
      health,
      attack,
      defense,
      speed,
      abilities=None
  ):
    super().__init__(
      name,
      character_class,
      health,
      attack,
      defense,
      speed,
      abilities
    )

    self.specialization = specialization