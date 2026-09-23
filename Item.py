from __future__ import annotations


class Item:
    def __init__(self,name: str, value: int):
        self.name = name
        self.value = value
    
    def clone(self) -> Item:
        """
        Creates a copy of the item.

        This prevents modifications to the original item template
        when the player interacts with items.

        Returns:
            Item: A new instance with identical attributes.
        """
        return Item(self.name,self.value)

    @staticmethod
    def getAllItems() -> list[Item]:
        """
        Returns a list of all available items in the game.

        Each item is predefined with a name and a value (cost).

        Returns:
            list: list containing all item objects.
        """
        return[
            Item("Heiltrank", 20),
            Item("Steroide", 45),
            Item("Gift", 1),
            Item("Rüstung", 40),
            Item("Buch des Wissens", 50),
            Item("Geheimnisvolles Artefakt", 75),
            Item("Fokus-Trank", 30),
            Item("Adrenalin-Ampulle", 35),
            Item("--Ausverkauft--", 0)
        ]