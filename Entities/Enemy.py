from __future__ import annotations
from Entities.Entity import Entity

class Enemy(Entity):
    def __init__(self, xp, boss, **kwargs):
        super().__init__(**kwargs)
        self.xp = xp
        self.boss = boss
    
    def clone(self) -> Enemy:
        """
        Creates a deep copy of the enemy.

        This ensures that the original template enemy is not modified during combat.

        Returns:
            Enemy: A new instance with identical attributes.
        """
        clonedEnemy = Enemy(
            name = self.name,
            hp = self.hp,
            damage = self.damage,
            level = self.level,
            gold = self.gold,
            xp = self.xp,
            maxHp = self.maxHp,
            boss = self.boss,
            effect = self.effect
        )

        return clonedEnemy
    
    @staticmethod
    def getPossibleEnemies() -> list[Enemy]:
        """
        Returns a list of all predefined enemies in the game.

        Includes both normal enemies and boss enemies.

        Returns:
            list: List of enemy templates.
        """
        return [
            Enemy(xp = 3, hp = 2, name = "Skelett", damage = 3, level = 1, gold = 3, maxHp = 2, effect = None, boss = False),
            Enemy(xp = 4, hp = 3, name = "Zombie", damage = 2, level = 1, gold = 3, maxHp = 3, effect  = None, boss = False),
			Enemy(xp = 7, hp = 5, name = "Golem", damage = 1, level = 1, gold = 5, maxHp = 5, effect = None, boss = False),
			Enemy(xp = 1, hp = 1, name = "Kobold", damage = 2, level = 1, gold = 4, maxHp = 1, effect = None, boss = False),
			Enemy(xp = 15, hp = 7, name = "Drache", damage = 5, level = 1, gold = 10, maxHp = 7, effect = None, boss = False),
			Enemy(xp = 8, hp = 2, name = "Magier", damage = 4, level = 1, gold = 1, maxHp = 2, effect = None, boss = False),
			Enemy(xp = 6, hp = 4, name = "Wolfsrudel", damage = 4, level = 1, gold = 6, maxHp = 4, effect = None, boss = False),
			Enemy(xp = 10, hp = 6, name = "Ork-Krieger", damage = 5, level = 1, gold = 8, maxHp = 6, effect = None, boss = False),
			Enemy(xp = 9, hp = 5, name = "Ghul", damage = 4, level = 1, gold = 7, maxHp = 5, effect = None, boss = False),
			Enemy(xp = 7, hp = 4, name = "Grottenwächter", damage = 3, level = 1, gold = 6, maxHp = 4, effect = "stun", boss = False), # Kann den Spieler betäuben
			Enemy(xp = 50, hp = 20, name = "Feuerriese", damage = 6, level = 1, gold = 30, maxHp = 20, effect = None, boss = True),
			Enemy(xp = 50, hp = 30, name = "Hydra", damage = 4, level = 1, gold = 30, maxHp = 30, effect = "regen", boss = True), # Regeneriert pro Runde HP
			Enemy(xp = 50, hp = 12, name = "Giftfrosch", damage = 10, level = 1, gold = 30, maxHp = 12, effect = "poison", boss = True), # Kann den Spieler vergiften
			Enemy(xp = 50, hp = 45, name = "Oger", damage = 7, level = 1, gold = 30, maxHp = 45, effect = None, boss = True),
			Enemy(xp = 55, hp = 25, name = "Lichkönig", damage = 8, level = 1, gold = 35, maxHp = 25, effect = "drain", boss = True), # Saugt bei Angriffen Leben ab
			Enemy(xp = 55, hp = 28, name = "Frostkoloss", damage = 6, level = 1, gold = 32, maxHp = 28, effect = "stun", boss = True) # Kann den Spieler betäuben
            ]