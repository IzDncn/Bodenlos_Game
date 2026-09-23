class Entity():
    def __init__(self, hp, name, damage, level, gold, maxHp, effect=None):
        self.hp = hp
        self.name = name
        self.damage = damage
        self.level = level
        self.gold = gold
        self.maxHp = maxHp
        self.baseHp = hp
        self.baseDamage = damage
        self.effect = effect

        # Vergiftungs-Statuseffekt (aktuell nur für Gegner genutzt, z.B. durch den Skill "Giftpfeil")
        self.poisonDamage = 0
        self.poisonTurns = 0

    def ApplyPoison(self, damage: int, turns: int) -> None:
        """
        Applies (or refreshes) a poison status effect on this entity.

        If the entity is already poisoned, the stronger damage value and
        the longer remaining duration are kept (poison doesn't stack additively).

        Args:
            damage (int): Poison damage dealt per turn.
            turns (int): Number of turns the poison lasts.
        """
        self.poisonDamage = max(self.poisonDamage, damage)
        self.poisonTurns = max(self.poisonTurns, turns)