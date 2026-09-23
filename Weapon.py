from __future__ import annotations


class Weapon:
    def __init__(self, name: str, damage: int, value: int, critChance: int = 0):
        self.name = name
        self.damage = damage          # Bonusschaden, der zum Grundschaden addiert wird
        self.value = value            # Preis beim Händler
        self.critChance = critChance  # Chance in % für einen kritischen Treffer (x2 Schaden)

    def clone(self) -> Weapon:
        """
        Creates a copy of the weapon.

        This prevents modifications to the original weapon template
        when the player equips it.

        Returns:
            Weapon: A new instance with identical attributes.
        """
        return Weapon(self.name, self.damage, self.value, self.critChance)

    @staticmethod
    def getAllWeapons() -> list[Weapon]:
        """
        Returns a list of all available weapons in the game.

        Each weapon is predefined with a name, a damage bonus, a value (cost)
        and an optional crit chance.

        Returns:
            list: list containing all weapon objects.
        """
        return [
            Weapon("Rostiger Dolch", damage=1, value=15, critChance=15),
            Weapon("Kurzschwert", damage=3, value=35, critChance=5),
            Weapon("Kriegshammer", damage=6, value=70, critChance=0),
            Weapon("Elfenbogen", damage=4, value=55, critChance=25),
            Weapon("Excalibur", damage=10, value=150, critChance=10),
            Weapon("Kriegssense", damage=8, value=120, critChance=8),
            Weapon("Assassinendolch", damage=2, value=45, critChance=35),
            Weapon("Kriegsaxt der Titanen", damage=12, value=180, critChance=5),
        ]
