from __future__ import annotations


class Armor:
    def __init__(self, name: str, defense: int, value: int):
        self.name = name
        self.defense = defense  # Schadensreduktion pro erhaltenem Treffer
        self.value = value      # Preis beim Händler

    def clone(self) -> Armor:
        """
        Creates a copy of the armor piece.

        This prevents modifications to the original armor template
        when the player equips it.

        Returns:
            Armor: A new instance with identical attributes.
        """
        return Armor(self.name, self.defense, self.value)

    @staticmethod
    def getAllArmor() -> list[Armor]:
        """
        Returns a list of all available armor pieces in the game.

        Each armor piece is predefined with a name, a defense value
        and a value (cost).

        Returns:
            list: list containing all armor objects.
        """
        return [
            Armor("Stoffrobe", defense=1, value=20),
            Armor("Lederrüstung", defense=2, value=40),
            Armor("Kettenhemd", defense=4, value=65),
            Armor("Plattenpanzer", defense=6, value=100),
            Armor("Drachenschuppenrüstung", defense=9, value=160),
            Armor("Obsidianrüstung", defense=7, value=130),
            Armor("Schattenmantel", defense=3, value=70),
            Armor("Wächterschild-Rüstung", defense=5, value=90),
        ]
