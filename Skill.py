from __future__ import annotations


class Skill:
    def __init__(self, name: str, cost: int, description: str, effectType: str, power: float):
        """
        Args:
            name (str): Display name of the skill.
            cost (int): Energy cost to use the skill.
            description (str): Flavor/explanation text shown to the player.
            effectType (str): "damage" (bonus attack), "damageAll" (bonus
                attack against every enemy), "heal" (restores hp), "poison"
                (damage over time), "buff" (temporary damage boost) or
                "shield" (temporary damage reduction) for the current fight.
            power (float): Multiplier/factor used to calculate the effect.
        """
        self.name = name
        self.cost = cost
        self.description = description
        self.effectType = effectType
        self.power = power

    @staticmethod
    def getAllSkills() -> list[Skill]:
        """
        Returns all skills that exist in the game, in the order in which
        they are learned (one per level-up, see Player.LearnSkill).

        Returns:
            list: list containing all skill objects.
        """
        return [
            Skill(
                name="Wuchtschlag",
                cost=4,
                description="Ein kraftvoller Schlag, der doppelten Schaden verursacht.",
                effectType="damage",
                power=2.0,
            ),
            Skill(
                name="Meditation",
                cost=3,
                description="Du sammelst deine Kräfte und heilst dich um 20% deiner maximalen HP.",
                effectType="heal",
                power=0.2,
            ),
            Skill(
                name="Kriegsschrei",
                cost=5,
                description="Du erhöhst deinen Schaden für den Rest des Kampfes um 50%.",
                effectType="buff",
                power=1.5,
            ),
            Skill(
                name="Präziser Stich",
                cost=6,
                description="Ein gezielter Stich, der garantiert kritisch trifft (dreifacher Schaden).",
                effectType="damage",
                power=3.0,
            ),
            Skill(
                name="Zweiter Atem",
                cost=7,
                description="Du heilst dich um 40% deiner maximalen HP.",
                effectType="heal",
                power=0.4,
            ),
            Skill(
                name="Adrenalinschub",
                cost=8,
                description="Ein Adrenalinschub lässt dich sofort mit 2,5-fachem Schaden zuschlagen.",
                effectType="damage",
                power=2.5,
            ),
            Skill(
                name="Eisenwille",
                cost=9,
                description="Du stählst deinen Willen und heilst dich um 30% deiner maximalen HP.",
                effectType="heal",
                power=0.3,
            ),
            Skill(
                name="Giftpfeil",
                cost=5,
                description="Ein giftiger Pfeil vergiftet den Gegner. Er erleidet über 3 Runden zusätzlichen Giftschaden.",
                effectType="poison",
                power=2.0,
            ),
            Skill(
                name="Wirbelangriff",
                cost=6,
                description="Ein wirbelnder Rundumschlag, der alle Gegner gleichzeitig trifft.",
                effectType="damageAll",
                power=1.2,
            ),
            Skill(
                name="Eisenhaut",
                cost=6,
                description="Du härtest deine Haut wie Eisen ab und reduzierst den Schaden, den du erleidest, für den Rest des Kampfes um 40%.",
                effectType="shield",
                power=0.4,
            ),
        ]
