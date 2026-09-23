from Entities.Entity import Entity
from random import randint
from Item import Item
from Weapon import Weapon
from Armor import Armor
from Skill import Skill
import os
import utils

clearConsole = utils.clearConsole

class Player(Entity):
    def __init__(self, nextLevel, levelProgress, progress, **kwargs):
        super().__init__(**kwargs)
        self.nextLevel = nextLevel
        self.levelProgress = levelProgress
        self.items = []
        self.progress = progress
        self.highScore = 0
        self.effect = [False, False]
        self.bossesDefeated = 0 # Zählt besiegte Bosse, u.a. für den Erfolg "Bossjäger"

        # Ausrüstung
        self.equippedWeapon: Weapon | None = None
        self.equippedArmor: Armor | None = None

        # Inventar für nicht ausgerüstete Waffen/Rüstungen (gesammelt, aber nicht aktiv)
        self.weaponInventory: list[Weapon] = []
        self.armorInventory: list[Armor] = []

        # Energie-Ressource für Skills
        self.maxEnergy = 10
        self.energy = self.maxEnergy

        # Erlernte Skills und temporärer Kampf-Buff (z.B. Kriegsschrei)
        self.skills: list[Skill] = []
        self.combatDamageMultiplier = 1.0
        self.combatDamageReduction = 1.0  # z.B. durch den Skill "Eisenhaut", 1.0 = keine Reduktion

        # Betäubung (z.B. durch Gegner mit effect == "stun") lässt die nächste Runde ausfallen
        self.stunned = False

    def RemoveUsedItem(self, items : list[Item]) -> list[Item]:
        """
        Allows the player to select and use an item from their inventory.

        The selected item is applied and then removed from the inventory.

        Args:
            items (list[Item]): The player's current inventory.

        Returns:
            list: Updated inventory after removing the used item.
        """
        clearConsole()
        invalid = True

        while invalid:
            i = 1
            for x in items: # Printing all Items the player has
                print(f"{i}: {x.name}")
                i += 1

            print(f"\nWelches Item willst du benutzen?:")
            choice = input("> ")

            try: # Check for error and wrong input
                choice = int(choice)
                if not (1 <= choice <= len(items)):
                    raise IndexError
                self.UseItem(items[choice - 1])
            except (ValueError, IndexError): # If input isn't valid
                clearConsole()
                print(f"Invalider Input! Bitte nochmal versuchen.\n")
            else: # If input is valid
                invalid = False
        
        items.pop(choice-1) # Removes Item
        return items
    
    def UseItem(self, item : Item) -> None:
        """
        Applies the effect of an item to the player.

        Supported effects:
        - Healing potion: restores health
        - Steroids: increases damage
        - Poison: reduces stats and inflicts damage
        - Armor: increases maximum HP
        - Knowledge book: increases XP gain
        - Mysterious artifact: random buff or debuff
        - Fokus-Trank: fully restores energy
        - Adrenalin-Ampulle: cures poison and stun

        Args:
            item (Item): The item to be used.
        """
        if item.name == "Heiltrank":
            # Heals the player
            self.hp += int(round(self.maxHp / 4, 0))
            if self.hp > self.maxHp:
                self.hp = self.maxHp
            print(f"\n{self.name} hat jetzt {self.hp} Lebenspunkte")
        
        if item.name == "Steroide":
            # Increases the players damage output (dauerhaft, kein Ablauf-Effekt nötig)
            self.damage += int(round(self.damage / 2, 0))
            print("\nDurch das Benutzen von speziellen Substanzen bist du so stark wie nie zuvor!")
        
        if item.name == "Gift":
            # Poisons and damages the player
            self.damage -= 1
            self.hp -= 5
            self.maxHp -= 5
            self.effect[0] = True
            print(f"\nDu wurdest vergiftet! Du hast jetzt nur noch {self.hp} Lebenspunkte")

        if item.name == "Rüstung":
            # Increases the players max hp
            self.maxHp += int(round(self.maxHp / 4, 0))
            print(f"\nDeine maximale HP liegt jetzt bei {self.maxHp}!")

        if item.name == "Buch des Wissens":
            # Increases the xp the player receives
            print("\nDurch das Studieren alter Texte erhältst du für kurze Zeit mehr Erfahrung.")
            self.effect[1] = True

        if item.name == "Geheimnisvolles Artefakt":
            # In- or decreases the players stats
            wheelOfLuck = randint(0,1)
            if wheelOfLuck == 0:
                print("\nDu hast Glück! Alle deine Stats wurden um 2 erhöht.")
                self.maxHp += 2
                self.hp += 2
                self.damage += 2
            else:
                print("\nDu hast einen Fluch beschworen! Alle deine Stats wurden um 1 verringert.")
                self.maxHp -= 1
                self.hp -= 1
                self.damage -= 1

        if item.name == "Fokus-Trank":
            # Restores the players energy fully, useful mid-fight
            self.energy = self.maxEnergy
            print(f"\nDeine Energie ist wieder vollständig aufgeladen ({self.energy}/{self.maxEnergy})!")

        if item.name == "Adrenalin-Ampulle":
            # Cures negative status effects (Vergiftung, Betäubung)
            hadEffect = self.poisonTurns > 0 or self.stunned
            self.poisonTurns = 0
            self.poisonDamage = 0
            self.stunned = False
            if hadEffect:
                print("\nEin Adrenalinschub befreit dich von allen negativen Statuseffekten!")
            else:
                print("\nDu spürst einen Adrenalinschub - momentan wirkt er allerdings ins Leere.")
        
        utils.slowPrint(f"\nDrücke Enter um fortzufahren...")
        input()
        
    def CheckForEffect(self):
        """
        Checks and updates active status effects on the player.

        Resets temporary effects after they expire and informs the player.
        """
        if self.effect[0] == True:
            self.effect[0] = False
            print(f"{self.name} ist nicht mehr vergiftet.")
        if self.effect[1] == True:
            self.effect[1] = False
            print("Du hast alles Wissen erlangt!")

    # ===== Ausrüstung =====

    def EquipWeapon(self, weapon: Weapon) -> None:
        """
        Equips a new weapon. If another weapon is already equipped,
        it is moved into the weapon inventory instead of being lost.

        Args:
            weapon (Weapon): The weapon to equip.
        """
        if self.equippedWeapon is not None:
            self.weaponInventory.append(self.equippedWeapon)
        self.equippedWeapon = weapon
        print(f"\nDu hast {weapon.name} ausgerüstet! (+{weapon.damage} Schaden)")

    def EquipArmor(self, armor: Armor) -> None:
        """
        Equips a new armor piece. If another armor piece is already
        equipped, it is moved into the armor inventory instead of being lost.

        Args:
            armor (Armor): The armor to equip.
        """
        if self.equippedArmor is not None:
            self.armorInventory.append(self.equippedArmor)
        self.equippedArmor = armor
        print(f"\nDu hast {armor.name} angelegt! (Verteidigung: {armor.defense})")

    def AddWeaponToInventory(self, weapon: Weapon) -> None:
        """
        Adds a weapon to the inventory without equipping it.

        Args:
            weapon (Weapon): The weapon to store.
        """
        self.weaponInventory.append(weapon)

    def AddArmorToInventory(self, armor: Armor) -> None:
        """
        Adds an armor piece to the inventory without equipping it.

        Args:
            armor (Armor): The armor to store.
        """
        self.armorInventory.append(armor)

    def SellWeapon(self, index: int) -> int:
        """
        Sells a weapon from the inventory for its listed value.

        Args:
            index (int): Index of the weapon in weaponInventory.

        Returns:
            int: The gold received for the weapon.
        """
        weapon = self.weaponInventory.pop(index)
        self.gold += weapon.value
        print(f"\nDu verkaufst {weapon.name} für {weapon.value} Gold!")
        return weapon.value

    def SellArmor(self, index: int) -> int:
        """
        Sells an armor piece from the inventory for its listed value.

        Args:
            index (int): Index of the armor piece in armorInventory.

        Returns:
            int: The gold received for the armor piece.
        """
        armor = self.armorInventory.pop(index)
        self.gold += armor.value
        print(f"\nDu verkaufst {armor.name} für {armor.value} Gold!")
        return armor.value

    def SellItem(self, index: int) -> int:
        """
        Sells an item from the inventory back to a trader.

        Unlike weapons and armor, items only fetch half their listed
        value, since they're consumables rather than reusable equipment.

        Args:
            index (int): Index of the item in items.

        Returns:
            int: The gold received for the item.
        """
        item = self.items.pop(index)
        refund = item.value // 2
        self.gold += refund
        print(f"\nDu verkaufst {item.name} für {refund} Gold!")
        return refund

    def SwitchWeapon(self, index: int) -> None:
        """
        Equips a weapon from the inventory by its index, swapping it
        with the currently equipped weapon (if any).

        Args:
            index (int): Index of the weapon in weaponInventory.
        """
        newWeapon = self.weaponInventory.pop(index)
        oldWeapon = self.equippedWeapon
        self.equippedWeapon = newWeapon
        if oldWeapon is not None:
            self.weaponInventory.append(oldWeapon)
        print(f"\nDu rüstest jetzt {newWeapon.name} aus!")

    def SwitchArmor(self, index: int) -> None:
        """
        Equips an armor piece from the inventory by its index, swapping it
        with the currently equipped armor (if any).

        Args:
            index (int): Index of the armor piece in armorInventory.
        """
        newArmor = self.armorInventory.pop(index)
        oldArmor = self.equippedArmor
        self.equippedArmor = newArmor
        if oldArmor is not None:
            self.armorInventory.append(oldArmor)
        print(f"\nDu legst jetzt {newArmor.name} an!")

    def GetAttackDamage(self) -> tuple[int, bool]:
        """
        Calculates the damage of a normal attack, including weapon bonus,
        temporary combat buffs and a possible critical hit.

        Returns:
            tuple[int, bool]: (dealt damage, whether it was a critical hit)
        """
        dmg = self.damage
        critChance = 0
        if self.equippedWeapon:
            dmg += self.equippedWeapon.damage
            critChance = self.equippedWeapon.critChance

        isCrit = critChance > 0 and randint(1, 100) <= critChance
        if isCrit:
            dmg *= 2

        dmg = int(round(dmg * self.combatDamageMultiplier))
        return dmg, isCrit

    def GetDefense(self) -> int:
        """
        Returns the flat damage reduction granted by the equipped armor.

        Returns:
            int: Defense value (0 if no armor is equipped).
        """
        return self.equippedArmor.defense if self.equippedArmor else 0

    # ===== Skills =====

    def LearnSkill(self, skill: Skill) -> None:
        """
        Adds a skill to the player's known skills, if not already known.

        Args:
            skill (Skill): The skill to learn.
        """
        if all(s.name != skill.name for s in self.skills):
            self.skills.append(skill)
            print(f"\nDu hast einen neuen Skill erlernt: {skill.name}!")
            utils.slowPrint(f"({skill.description})")

    def RegenEnergy(self, amount: int = 2) -> None:
        """
        Regenerates the player's energy, capped at maxEnergy.

        Args:
            amount (int): Amount of energy restored.
        """
        self.energy = min(self.maxEnergy, self.energy + amount)

    def UseSkill(self, skill: Skill, target=None) -> str:
        """
        Applies the effect of a skill. Costs energy.

        Supported effect types:
        - "damage": deals bonus damage to a single target
        - "damageAll": deals bonus damage to every living enemy at once
        - "heal": restores a percentage of the player's max hp
        - "poison": inflicts a poison status effect on a single target
        - "buff": temporarily multiplies the player's attack damage
          for the rest of the current fight
        - "shield": temporarily reduces the damage the player takes
          for the rest of the current fight

        Args:
            skill (Skill): The skill to use.
            target: The enemy (or, for "damageAll", the list of alive
                enemies) targeted by a damage skill, if applicable.

        Returns:
            str: A short message describing what happened.
        """
        self.energy -= skill.cost

        if skill.effectType == "damage" and target is not None:
            dmg = int(round((self.damage + (self.equippedWeapon.damage if self.equippedWeapon else 0)) * skill.power))
            dmg = int(round(dmg * self.combatDamageMultiplier))
            target.hp -= dmg
            return f"{skill.name} trifft {target.name} für {dmg} Schaden!"

        if skill.effectType == "damageAll" and target is not None:
            dmg = int(round((self.damage + (self.equippedWeapon.damage if self.equippedWeapon else 0)) * skill.power))
            dmg = int(round(dmg * self.combatDamageMultiplier))
            for enemy in target: # 'target' ist hier die Liste aller lebenden Gegner
                enemy.hp -= dmg
            return f"{skill.name} trifft alle Gegner für je {dmg} Schaden!"

        if skill.effectType == "poison" and target is not None:
            poisonTurns = 3
            poisonDmg = max(1, int(round(skill.power + self.level - 1)))
            target.ApplyPoison(damage=poisonDmg, turns=poisonTurns)
            return f"{skill.name} vergiftet {target.name}! ({poisonDmg} Schaden pro Runde für {poisonTurns} Runden)"

        if skill.effectType == "heal":
            healAmount = int(round(self.maxHp * skill.power))
            self.hp = min(self.maxHp, self.hp + healAmount)
            return f"{skill.name} heilt dich um {healAmount} Lebenspunkte!"

        if skill.effectType == "buff":
            self.combatDamageMultiplier *= skill.power
            return f"{skill.name} erhöht deinen Schaden für den Rest des Kampfes!"

        if skill.effectType == "shield":
            self.combatDamageReduction *= max(0.0, 1 - skill.power)
            return f"{skill.name} reduziert den Schaden, den du erleidest, für den Rest des Kampfes um {int(skill.power * 100)}%!"

        return f"{skill.name} hatte keine Wirkung."

    def ResetCombatBuffs(self) -> None:
        """
        Resets temporary combat-only state: buffs (e.g. from Kriegsschrei),
        the shield damage-reduction (e.g. from Eisenhaut), any remaining
        poison status and a lingering stun, so nothing carries over into
        the next, unrelated fight.

        Called after a fight ends.
        """
        self.combatDamageMultiplier = 1.0
        self.combatDamageReduction = 1.0
        self.poisonDamage = 0
        self.poisonTurns = 0
        self.stunned = False