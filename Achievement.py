from __future__ import annotations


class Achievement:
    def __init__(self, id: str, name: str, description: str, goal: int, statKey: str):
        """
        Args:
            id (str): Stabile, sprechende ID. Wird in achievements.json
                gespeichert, damit Erfolge über mehrere Spielstände hinweg
                freigeschaltet bleiben.
            name (str): Anzeigename.
            description (str): Erklärt, wie der Erfolg freigeschaltet wird.
            goal (int): Schwellenwert, den der beobachtete Wert erreichen muss.
            statKey (str): Welcher Spieler-Wert geprüft wird. Eines von
                "level", "gold", "highScore", "bossesDefeated", "skills".
        """
        self.id = id
        self.name = name
        self.description = description
        self.goal = goal
        self.statKey = statKey

    def IsUnlocked(self, player) -> bool:
        """
        Prüft, ob der Spieler den geforderten Wert bereits erreicht hat.

        Args:
            player (Player): Die Spielerinstanz.

        Returns:
            bool: True, wenn der beobachtete Wert >= goal ist.
        """
        currentValue = {
            "level": player.level,
            "gold": player.gold,
            "highScore": player.highScore,
            "bossesDefeated": player.bossesDefeated,
            "skills": len(player.skills),
        }.get(self.statKey, 0)

        return currentValue >= self.goal

    @staticmethod
    def getAllAchievements() -> list[Achievement]:
        """
        Returns a list of all achievements that exist in the game.

        Jeder Erfolg ist mit einer ID, einem Namen, einer Beschreibung
        und einer Freischalt-Bedingung vordefiniert.

        Returns:
            list: list containing all achievement objects.
        """
        return [
            Achievement("erste_schritte", "Erste Schritte", "Erreiche Level 2.", goal=2, statKey="level"),
            Achievement("veteran", "Veteran", "Erreiche Level 5.", goal=5, statKey="level"),
            Achievement("legende", "Legende", "Erreiche Level 10.", goal=10, statKey="level"),
            Achievement("wohlhabend", "Wohlhabend", "Besitze gleichzeitig 100 Gold.", goal=100, statKey="gold"),
            Achievement("steinreich", "Steinreich", "Besitze gleichzeitig 300 Gold.", goal=300, statKey="gold"),
            Achievement("entdecker", "Entdecker", "Schließe 10 Encounter ab.", goal=10, statKey="highScore"),
            Achievement("weitgereist", "Weitgereist", "Schließe 25 Encounter ab.", goal=25, statKey="highScore"),
            Achievement("bossjaeger", "Bossjäger", "Besiege deinen ersten Boss.", goal=1, statKey="bossesDefeated"),
            Achievement("bosstoeter", "Bosstöter", "Besiege 3 Bosse.", goal=3, statKey="bossesDefeated"),
            Achievement("gelehrter", "Gelehrter", "Erlerne 3 Skills.", goal=3, statKey="skills"),
        ]
