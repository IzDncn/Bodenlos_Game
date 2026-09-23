from __future__ import annotations
import random 
import os
from time import sleep
from Entities.Enemy import Enemy
from Entities.Player import Player
from Weapon import Weapon
from Armor import Armor
from Skill import Skill
import utils
from colorama import Fore, Style, init
init(autoreset=True)

clearConsole = utils.clearConsole

class Encounter:
    # Obergrenzen der Zufallswerte (0..upperBound) je Raumtyp, siehe RoomDescription/ClassifyRoom.
    # Ein Wert fällt in einen Raumtyp, wenn er <= der jeweiligen Grenze liegt.
    ROOM_ENEMY_MAX = 39
    ROOM_CHEST_MAX = 54
    ROOM_CAMPFIRE_MAX = 59
    ROOM_TRAP_MAX = 63
    ROOM_TRADER_MAX = 89
    # Alles darüber (bis upperBound) ist ein Boss-Raum

    SCALING_INTERVAL = 8 # Nach so vielen abgeschlossenen Encountern werden Gegner stärker (siehe Scaling)

    def __init__(self, name: str = ""):
        self.name = name
        self.lastRoomType = None # Merkt sich den letzten Raumtyp, um Wiederholungen bei Truhe/Trader/Boss zu vermeiden
    
    # ===== MAIN-LOOP =====

    @staticmethod
    def MainLoop(player,encounter: Encounter, possibleEnemies: list[Enemy], allItems: list,
                 allWeapons: list[Weapon] = None, allArmor: list[Armor] = None) -> None:
        """
        Main game loop for handling a single room encounter.

        Randomly determines which type of room the player encounters:
        - Enemy fight
        - Chest (loot)
        - Campfire (rest)
        - Trap
        - Trader
        - Boss fight

        Executes the corresponding logic for the selected encounter.

        Args:
            player (Player): The current player instance.
            encounter (Encounter): The encounter handler instance.
            possibleEnemies (list[Enemy]): List of all possible enemies.
            allItems (list[Item]): List of all available items.
            allWeapons (list[Weapon]): List of all available weapons.
            allArmor (list[Armor]): List of all available armor pieces.
        """
        allWeapons = allWeapons or []
        allArmor = allArmor or []
        roomDescription = encounter.RoomDescription(player)
        levelUp = False
        sleep(1)

        if roomDescription <= encounter.ROOM_ENEMY_MAX: # Enemies
            "The player encounters a group of enemies"
            enemyNumber = encounter.EnemyNumber(player) # Chooses how many enemies attack
            enemies = encounter.EnemySelection(possibleEnemies, enemyNumber) # Chooses the attacking enemies
            newEnemies = enemies

            clearConsole()
            sleep(0.25)
            print("\nDu wirst von einer Gruppe von Monstern angegriffen!")
            sleep(1)

            while len(newEnemies) != 0 and player.hp > 0: # Until all enemies or the player dies
                i = encounter.PlayerMoveChoice(newEnemies, player)
                if i == 1:
                    player.progress += 1
                    break

                encounter.TickStatusEffects(enemies, player)
                if player.hp <= 0: # Vergiftung kann den Spieler bereits hier töten
                    break

                newEnemies = []
                for e in enemies: # Updating the enemies list
                    if e.hp > 0:
                        newEnemies.append(e)

                levelUp = encounter.CheckForLevel(player.levelProgress, player.nextLevel) # Checking for level up
                if levelUp: # Act accordingly
                    player = encounter.LevelUp(player)
                    levelUp = False

                if len(newEnemies) != 0:
                    encounter.EnemyAttack(newEnemies, player)
                elif len(newEnemies) == 0:
                    print(f"\nDu hast alle Gegner getötet!")
                    player.progress += 1
                    player.highScore += 1
                    sleep(1.5)

            player.ResetCombatBuffs() # Temporäre Kampf-Buffs (z.B. Kriegsschrei) laufen aus
            player.CheckForEffect() # Temporäre Item-Effekte (z.B. Gift, Buch des Wissens) laufen aus

        if encounter.ROOM_ENEMY_MAX < roomDescription <= encounter.ROOM_CHEST_MAX: # Chest
            "The players finds a chest"
            encounter.Chest(player, allWeapons, allArmor)
            player.progress += 1
            player.highScore += 1

        if encounter.ROOM_CHEST_MAX < roomDescription <= encounter.ROOM_CAMPFIRE_MAX: # Campfire
            "The player finds a campfire to rest at"
            encounter.Campfire(player)
            player.progress += 1

        if encounter.ROOM_CAMPFIRE_MAX < roomDescription <= encounter.ROOM_TRAP_MAX: # Trap
            "The player stumbles into a trap"
            encounter.Trap(player)
            player.progress += 1

        if encounter.ROOM_TRAP_MAX < roomDescription <= encounter.ROOM_TRADER_MAX: # Trader
            "The player meets a trader"
            encounter.Trader(player, allItems, allWeapons, allArmor)
            player.progress += 1
            player.highScore += 1

        if encounter.ROOM_TRADER_MAX < roomDescription: # Boss
            "The player encounters a boss"
            bossDefeated = encounter.Boss(possibleEnemies, player, encounter)
            if bossDefeated: # Bei einer Niederlage gibt es keinen Fortschritt
                player.progress += 1
                player.highScore += 1

    # ===== Encounter-Helfer =====

    def ClassifyRoom(self, roomDescription: int) -> str:
        """
        Translates a raw RoomDescription roll into its room type label.

        Args:
            roomDescription (int): The rolled value.

        Returns:
            str: One of "Enemy", "Chest", "Campfire", "Trap", "Trader", "Boss".
        """
        if roomDescription <= self.ROOM_ENEMY_MAX:
            return "Enemy"
        elif roomDescription <= self.ROOM_CHEST_MAX:
            return "Chest"
        elif roomDescription <= self.ROOM_CAMPFIRE_MAX:
            return "Campfire"
        elif roomDescription <= self.ROOM_TRAP_MAX:
            return "Trap"
        elif roomDescription <= self.ROOM_TRADER_MAX:
            return "Trader"
        else:
            return "Boss"

    def RoomDescription(self, player) -> int:
        """
        Determines what type of room the player will encounter.

        The probabilities depend on the player's current score.
        Enemy fights may repeat back to back, but Chest/Campfire/Trap/Trader/Boss
        rooms are re-rolled if they would repeat the previous room type,
        so the player doesn't run into the same special room twice in a row.

        Args:
            player (Player): The player instance.

        Returns:
            int: A random value used to determine the encounter type.
        """
        if player.highScore <= 1: # Setting the probabilities according to the current score
            upperBound = 64
        elif player.highScore <= 4: # Increases the probability of a trader
            upperBound = 89
        else: # A boss can appear after the 5th encounter
            upperBound = 99

        roomDescription = random.randint(0, upperBound)
        roomType = self.ClassifyRoom(roomDescription)

        # Truhe/Lagerfeuer/Falle/Trader/Boss sollen nicht zweimal in Folge auftauchen
        attempts = 0
        while roomType in ("Chest", "Campfire", "Trap", "Trader", "Boss") and roomType == self.lastRoomType and attempts < 15:
            roomDescription = random.randint(0, upperBound)
            roomType = self.ClassifyRoom(roomDescription)
            attempts += 1

        self.lastRoomType = roomType
        return roomDescription
     
    def EnemyNumber(self, player) -> int:
        """
        Determines how many enemies the player will encounter.

        The number increases with the player's progress.

        Args:
            player (Player): The player instance.

        Returns:
            int: Number of enemies to spawn.
        """
        if player.highScore <= 4:
            enemyNumber = random.randint(1, 4)
        elif player.highScore <= 7: # Increases the possible number after the 5th encounter
            enemyNumber = random.randint(2, 5)
        else: # Increases the possible number of enemies 
            enemyNumber = random.randint(2, 6)
        return enemyNumber

    def PlayerCreator(self) -> Player:
        """
        Creates and initializes a new player character.

        Prompts the user for a name and sets default starting stats.

        Returns:
            Player: A fully initialized player instance.
        """
        clearConsole()

        print("=========================")
        print(Fore.CYAN + Style.BRIGHT + "        BODENLOS         ")
        print("=========================")
        print(Style.RESET_ALL)

        utils.slowPrint("Willkommen, Reisender...")
        sleep(1)

        print("\nWas ist dein Name?")
        playerName = input("> ")
        # Making a new player object
        player = Player(
            name = playerName,
            hp = 20,
            damage = 3,
            level = 1,
            gold = 10,
            levelProgress = 0,
            nextLevel = 30,
            progress = 0,
            maxHp = 20,
        )

        print(Fore.GREEN + f"\nWillkommen, {player.name}!")
        return player
    
    def ShowEnemies(self, enemies) -> None:
        """
        Displays all currently alive enemies with their stats.

        Args:
            enemies (list[Enemy]): List of active enemies.
        """
        print(Fore.RED + "\n=== Gegner ===")

        for i, enemy in enumerate(enemies, start=1):
            poisonTag = f" {Fore.GREEN}[Vergiftet]{Style.RESET_ALL}" if enemy.poisonTurns > 0 else ""
            print(
                f"{i}. {enemy.name:<12} "
                f"Leben: {enemy.hp}/{enemy.maxHp} | "
                f"Schaden: {enemy.damage}"
                f"{poisonTag}"
            )

    def EnemySelection(self, possibleEnemies: list[Enemy], enemyNumber) -> list[Enemy]:
        """
        Selects a group of enemies for an encounter.

        Randomly picks enemies from the available pool and returns clones
        to prevent modification of the original enemy templates.

        Args:
            possibleEnemies (list[Enemy]): List of all available enemies.
            enemyNumber (int): Number of enemies to spawn.

        Returns:
            list: List of selected enemy instances.
        """
        enemies: list[Enemy] = []
        normalEnemies = [e for e in possibleEnemies if not e.boss] # Only choose from actual enemies, not bosses
        pool = normalEnemies or possibleEnemies # Fallback, if list contains only bosses
        for _ in range(enemyNumber):
            pick = random.choice(pool)
            enemies.append(pick.clone())
        return enemies
    
    def PlayerMoveChoice(self, enemies: list[Enemy], player) -> int:
        """
        Handles the player's turn during combat.

        The player can choose between:
        1 = Attack
        2 = Use item
        3 = Use skill (if any are learned)
        4 = Run away

        Repeats until a valid input is given.

        Args:
            enemies (list[Enemy]): List of active enemies.
            player (Player): The player instance.

        Returns:
            int:
                1 -> Player successfully escaped
                0 -> Normal action was performed
        """
        player.RegenEnergy() # Energie regeneriert sich jede Runde etwas

        if player.stunned: # Betäubung (z.B. durch den Grottenwächter/Frostkoloss) kostet genau eine Runde
            player.stunned = False
            clearConsole()
            print(Fore.RED + f"\nDu bist betäubt und kannst diese Runde nichts tun!")
            sleep(1)
            return 0

        while True:
            self.ShowEnemies(enemies) # Displays enemies
            utils.showPlayer(player)
            moveIsPossible = True
            print(Fore.CYAN + "\nWas willst du machen?")
            print(" [1] Angreifen")
            print(" [2] Item benutzen")
            print(" [3] Skill benutzen")
            print(" [4] Wegrennen")
            choice = input("> ")

            if choice == "1":
                "Player chooses to attack the enemies"
                clearConsole()
                self.ShowEnemies(enemies)
                utils.showPlayer(player)
                utils.printBox(f"Welchen Gegner möchtest du angreifen?")
                # Check if input is an integer
                try:
                    idx = int(input("> "))
                except ValueError:
                    clearConsole()
                    print("Invalider Input!\n")
                    moveIsPossible = False
                    if not moveIsPossible:
                        continue

                if 0 < idx <= len(enemies):
                    clearConsole()
                    target = enemies[idx - 1]
                    dmg, isCrit = player.GetAttackDamage()
                    target.hp -= dmg

                    if target.hp <= 0: # Player kills the enemy
                        
                        print(f"\nDu hast {target.name} getötet!")
                        print(Fore.YELLOW + f"+{target.gold} Gold")
                        player.gold += target.gold
                        if not player.effect[1]: # Check if xp buff is active
                            player.levelProgress += target.xp
                            print(Fore.GREEN + f"+{target.xp} XP")
                        else:
                            gained = 3 * target.xp
                            player.levelProgress += gained
                            print(Fore.GREEN + f"Das Buch des Wissens hat sich ausgezahlt!\n+{gained} XP")
                    else: # Enemy takes damage
                        critText = " (KRITISCHER TREFFER!)" if isCrit else ""
                        print(Fore.YELLOW + f"\n{target.name} nimmt {dmg} Schaden!{critText}")
                else:
                    clearConsole()
                    print("Invalider Input! Bitte nochmal versuchen.\n")
                    moveIsPossible = False
            
            elif choice == "2":
                "Player chooses to use an Item"
                clearConsole()
                if len(player.items) > 0:
                    player.items = player.RemoveUsedItem(player.items)
                else:
                    print("\nDu hast keine Items im Inventar (Du kannst Items beim Händler kaufen)\n")
                    moveIsPossible = False

            elif choice == "3":
                "Player chooses to use a skill"
                clearConsole()
                if len(player.skills) == 0:
                    print("\nDu hast noch keine Skills erlernt (Skills werden bei einem Level-Up freigeschaltet).\n")
                    moveIsPossible = False
                else:
                    self.ShowEnemies(enemies)
                    utils.showPlayer(player)
                    print(Fore.MAGENTA + f"\n=== Skills (Energie: {player.energy}/{player.maxEnergy}) ===")
                    for i, s in enumerate(player.skills, start=1):
                        print(f" [{i}] {s.name} (Kosten: {s.cost}) - {s.description}")

                    skillChoice = input("> ")
                    try:
                        sIdx = int(skillChoice)
                        if not (1 <= sIdx <= len(player.skills)):
                            raise IndexError
                        skill = player.skills[sIdx - 1]
                    except (ValueError, IndexError):
                        clearConsole()
                        print("Invalider Input!\n")
                        moveIsPossible = False
                        skill = None

                    if skill is not None:
                        if player.energy < skill.cost:
                            clearConsole()
                            print("\nDu hast nicht genug Energie für diesen Skill!\n")
                            moveIsPossible = False
                        else:
                            clearConsole()
                            target = None
                            if skill.effectType in ("damage", "poison"):
                                self.ShowEnemies(enemies)
                                utils.printBox("Welchen Gegner möchtest du anvisieren?")
                                try:
                                    tIdx = int(input("> "))
                                    if not (1 <= tIdx <= len(enemies)):
                                        raise IndexError
                                    target = enemies[tIdx - 1]
                                except (ValueError, IndexError):
                                    clearConsole()
                                    print("Invalider Input!\n")
                                    moveIsPossible = False
                                    target = "invalid"
                            elif skill.effectType == "damageAll":
                                # Flächenschaden braucht keine Zielauswahl, trifft alle lebenden Gegner
                                target = [e for e in enemies if e.hp > 0]

                            if target != "invalid":
                                clearConsole()
                                message = player.UseSkill(skill, target)
                                print(Fore.MAGENTA + f"\n{message}")

                                if isinstance(target, list): # Flächenschaden: mehrere Gegner können gleichzeitig sterben
                                    for e in target:
                                        if e.hp <= 0:
                                            print(f"\nDu hast {e.name} getötet!")
                                            print(Fore.YELLOW + f"+{e.gold} Gold")
                                            player.gold += e.gold
                                            if not player.effect[1]:
                                                player.levelProgress += e.xp
                                                print(Fore.GREEN + f"+{e.xp} XP")
                                            else:
                                                gained = 3 * e.xp
                                                player.levelProgress += gained
                                                print(Fore.GREEN + f"Das Buch des Wissens hat sich ausgezahlt!\n+{gained} XP")
                                elif target is not None and target.hp <= 0:
                                    print(f"\nDu hast {target.name} getötet!")
                                    print(Fore.YELLOW + f"+{target.gold} Gold")
                                    player.gold += target.gold
                                    if not player.effect[1]:
                                        player.levelProgress += target.xp
                                        print(Fore.GREEN + f"+{target.xp} XP")
                                    else:
                                        gained = 3 * target.xp
                                        player.levelProgress += gained
                                        print(Fore.GREEN + f"Das Buch des Wissens hat sich ausgezahlt!\n+{gained} XP")

            elif choice == "4":
                "Player tries to run away"
                clearConsole()
                roll = random.randint(1,100)
                if roll >= len(enemies) * 20 and not enemies[0].boss:
                    print("\nDu konntest entkommen!")
                    return 1
                elif roll >= 80:
                    print("\nDu konntest entkommen!")
                    return 1
                else:
                    print("\nDu konntest nicht entkommen!")
                
            else:
                clearConsole()
                print("Invalider Input! Bitte nochmal versuchen.\n")
                moveIsPossible = False
            
            sleep(0.5)
            if moveIsPossible:
                break

    def TickStatusEffects(self, enemies: list[Enemy], player) -> None:
        """
        Processes per-round status effects for both sides of a fight:

        - Vergiftung: der Spieler UND vergiftete Gegner erleiden Schaden
          über Zeit (siehe Entity.ApplyPoison). Wird ein Gegner dadurch
          getötet, erhält der Spieler dessen Gold/XP wie bei einem
          normalen Kill.
        - Regeneration: Gegner mit effect == "regen" (z.B. die Hydra)
          heilen sich pro Runde um einen Teil ihrer maximalen HP.

        Args:
            enemies (list[Enemy]): List of enemies (alive or dead) to check.
            player (Player): The player instance, for gold/XP rewards
                and for its own poison status.
        """
        if player.poisonTurns > 0:
            dmg = player.poisonDamage
            player.hp -= dmg
            player.poisonTurns -= 1
            print(Fore.RED + f"\nDu erleidest {dmg} Giftschaden!")
            if player.hp <= 0:
                print(Fore.RED + "Das Gift hat dich das Leben gekostet...")
            elif player.poisonTurns == 0:
                print(Fore.GREEN + "Deine Vergiftung klingt ab.")

        for e in enemies:
            if e.hp <= 0:
                continue

            if e.poisonTurns > 0:
                dmg = e.poisonDamage
                e.hp -= dmg
                e.poisonTurns -= 1
                print(Fore.GREEN + f"\n{e.name} erleidet {dmg} Giftschaden!")

                if e.hp <= 0:
                    print(f"Das Gift hat {e.name} getötet!")
                    print(Fore.YELLOW + f"+{e.gold} Gold")
                    player.gold += e.gold
                    if not player.effect[1]:
                        player.levelProgress += e.xp
                        print(Fore.GREEN + f"+{e.xp} XP")
                    else:
                        gained = 3 * e.xp
                        player.levelProgress += gained
                        print(Fore.GREEN + f"Das Buch des Wissens hat sich ausgezahlt!\n+{gained} XP")
                    continue
                elif e.poisonTurns == 0:
                    print(Fore.GREEN + f"Die Vergiftung von {e.name} klingt ab.")

            if e.effect == "regen" and e.hp < e.maxHp:
                heal = max(1, int(round(e.maxHp * 0.1)))
                e.hp = min(e.maxHp, e.hp + heal)
                print(Fore.CYAN + f"{e.name} regeneriert {heal} Lebenspunkte!")
        sleep(0.5)

    def EnemyAttack(self, enemies:list[Enemy], player) -> None:
        """
        Executes an attack from a random enemy on the player.

        Manche Gegner haben eine besondere Fähigkeit (siehe Enemy.effect),
        die zusätzlich zum normalen Angriff ausgelöst werden kann:
        - "poison": vergiftet den Spieler mit einer Chance von 40%
        - "drain": der Gegner heilt sich um einen Teil des angerichteten Schadens
        - "stun": betäubt den Spieler mit einer Chance von 35% (kostet eine Runde)

        Args:
            enemies (list[Enemy]): List of alive enemies.
            player (Player): The player instance.
        """
        attackingEnemy = random.randint(0,len(enemies) - 1) # Determines what enemy attacks
        e = enemies[attackingEnemy]

        
        dmgTaken = max(1, e.damage - player.GetDefense()) # Rüstung reduziert den Schaden, minimum 1
        dmgTaken = max(1, int(round(dmgTaken * player.combatDamageReduction))) # z.B. durch den Skill "Eisenhaut"

        print(Fore.RED + f"\n{e.name} greift dich an!")
        sleep(0.5)
        if player.GetDefense() > 0:
            print(Fore.RED + f"Deine Rüstung blockt {min(e.damage, player.GetDefense())} Schaden!")
        if player.combatDamageReduction < 1.0:
            print(Fore.CYAN + f"Dein Schild dämpft den Schlag weiter ab!")
        print(Fore.RED + f"Du erleidest {dmgTaken} Schaden!")
        player.hp -= dmgTaken

        if e.effect == "poison" and random.randint(1, 100) <= 40:
            poisonDmg = max(1, round(e.damage / 2))
            player.ApplyPoison(damage=poisonDmg, turns=3)
            print(Fore.GREEN + f"{e.name} vergiftet dich! ({poisonDmg} Schaden pro Runde für 3 Runden)")

        if e.effect == "drain" and e.hp < e.maxHp:
            healed = max(1, round(dmgTaken / 2))
            e.hp = min(e.maxHp, e.hp + healed)
            print(Fore.MAGENTA + f"{e.name} saugt {healed} Lebenspunkte von dir ab!")

        if e.effect == "stun" and random.randint(1, 100) <= 35:
            player.stunned = True
            print(Fore.YELLOW + f"{e.name} betäubt dich! Du verpasst deinen nächsten Zug.")

        sleep(1.5)
        clearConsole()

    def Campfire(self, player) -> None:
        """
        Handles a campfire (rest) encounter.

        The player rests at a campfire, restoring a portion of their
        missing HP and fully regenerating their energy.

        Args:
            player (Player): The player instance.
        """
        clearConsole()
        sleep(0.25)
        utils.printBox("Du findest ein verlassenes Lagerfeuer.")

        healAmount = int(round((player.maxHp - player.hp) * 0.5))
        player.hp = min(player.maxHp, player.hp + healAmount)
        player.energy = player.maxEnergy

        print(Fore.GREEN + f"\nDu rastest kurz und heilst {healAmount} Lebenspunkte.")
        print(Fore.MAGENTA + f"Deine Energie ist wieder vollständig aufgeladen ({player.energy}/{player.maxEnergy}).")
        input(f"\nDrücke Enter um fortzufahren...")

    def Trap(self, player) -> None:
        """
        Handles a trap encounter.

        The player stumbles into a hidden trap while exploring. There's
        a chance to spot it in time and avoid it entirely; otherwise it
        either deals damage (reduced by the player's armor, like a normal
        hit) or steals some of the player's gold.

        Args:
            player (Player): The player instance.
        """
        clearConsole()
        sleep(0.25)
        utils.printBox("Du stolperst in eine Falle!")
        sleep(0.5)

        roll = random.randint(1, 100)
        if roll <= 20: # Falle rechtzeitig bemerkt, kein Schaden
            print(Fore.GREEN + "\nIm letzten Moment weichst du aus und bleibst unversehrt!")
        elif roll <= 65: # Schadensfalle, Rüstung reduziert den Schaden wie im Kampf
            dmg = max(1, int(round(player.maxHp * 0.15)) - player.GetDefense())
            player.hp -= dmg
            print(Fore.RED + f"\nEin Pfeilhagel durchbohrt dich! Du erleidest {dmg} Schaden.")
            if player.hp <= 0:
                print(Fore.RED + "Die Falle hat dich das Leben gekostet...")
        else: # Goldfalle
            lost = min(player.gold, random.randint(5, 25))
            player.gold -= lost
            print(Fore.RED + f"\nEin hinterhältiger Dieb schnappt sich {Fore.YELLOW}{lost} Gold{Fore.RED}, bevor du reagieren kannst!")

        input(f"\nDrücke Enter um fortzufahren...")

    def Chest(self, player, allWeapons: list = None, allArmor: list = None) -> None:
        """
        Handles a chest encounter.

        The player receives a random amount of gold and experience points,
        and has a small chance of finding a weapon or armor piece as well.

        Args:
            player (Player): The player instance.
            allWeapons (list[Weapon]): List of all possible weapons.
            allArmor (list[Armor]): List of all possible armor pieces.
        """
        allWeapons = allWeapons or []
        allArmor = allArmor or []

        gold = random.randint(5,100)
        xp = random.randint(2,40)
        clearConsole()
        sleep(0.25)
        utils.printBox("Du hast eine Truhe gefunden!")

        print(f"+{Fore.YELLOW}{gold} Gold")
        print(f"+{Fore.CYAN}{xp} XP")

        player.gold += gold
        player.levelProgress += xp

        # Kleine Chance auf zusätzliche Ausrüstung in der Truhe
        lootRoll = random.randint(1, 100)
        if lootRoll <= 15 and allWeapons:
            loot = random.choice(allWeapons).clone()
            print(Fore.GREEN + f"\nZusätzlich findest du eine Waffe: {loot.name}!")
            if player.equippedWeapon is None:
                player.EquipWeapon(loot)
            else:
                player.AddWeaponToInventory(loot)
                compareText = self.CompareWeapon(loot, player.equippedWeapon)
                print(f"({loot.name} wurde deinem Inventar hinzugefügt{compareText})")
        elif lootRoll <= 30 and allArmor:
            loot = random.choice(allArmor).clone()
            print(Fore.GREEN + f"\nZusätzlich findest du eine Rüstung: {loot.name}!")
            if player.equippedArmor is None:
                player.EquipArmor(loot)
            else:
                player.AddArmorToInventory(loot)
                compareText = self.CompareArmor(loot, player.equippedArmor)
                print(f"({loot.name} wurde deinem Inventar hinzugefügt{compareText})")

        levelUp = self.CheckForLevel(player.levelProgress, player.nextLevel) # Check if player has enough xp to level up
        input(f"\nDrücke Enter um fortzufahren...")
        if levelUp:
            player = self.LevelUp(player)
    
    def CheckForLevel(self, levelProgress: int, nextLevel: int) -> bool:
        """
        Checks whether the player has gained enough experience to level up.

        Args:
            levelProgress (int): Current accumulated experience points.
            nextLevel (int): Required experience points for next level.

        Returns:
            bool: True if player can level up, otherwise False.
        """
        return levelProgress >= nextLevel
    
    def LevelUp(self,player) -> Player:
        """
        Levels up the player and increases their stats.

        Changes applied:
        - Level increases by 1
        - Maximum HP increases
        - Damage increases
        - XP requirement for next level increases

        Args:
            player (Player): The player instance.

        Returns:
            Player: The updated player.
        """
        player.level += 1
        player.levelProgress = 0
        player.maxHp += 5
        player.hp = player.maxHp
        player.damage += 1
        player.nextLevel += 20
        player.maxEnergy += 1
        player.energy = player.maxEnergy

        print(
            f"\n{player.name} ist jetzt Level {player.level}!"
            f"\nDu hast jetzt {player.maxHp} maximale HP."
            f"\nDu verursachst jetzt {player.damage} Schaden."
        )

        # Schaltet nach und nach neue Skills aus dem Skill-Pool frei
        allSkills = Skill.getAllSkills()
        unlearned = [s for s in allSkills if all(s.name != known.name for known in player.skills)]
        if unlearned:
            choices = random.sample(unlearned, min(2, len(unlearned)))
            if len(choices) == 1:
                player.LearnSkill(choices[0])
            else:
                print(Fore.MAGENTA + "\nWähle einen neuen Skill:")
                for i, s in enumerate(choices, start=1):
                    print(f" [{i}] {s.name} (Kosten: {s.cost}) - {s.description}")
                while True:
                    pick = input("> ").strip()
                    try:
                        pickIdx = int(pick)
                        if not (1 <= pickIdx <= len(choices)):
                            raise IndexError
                        break
                    except (ValueError, IndexError):
                        print("Invalider Input! Bitte nochmal versuchen.\n")
                player.LearnSkill(choices[pickIdx - 1])

        utils.slowPrint(f"\nDrücke Enter um fortzufahren...")
        input()
        return player
    
    def CompareWeapon(self, weapon: Weapon, equipped: Weapon | None) -> str:
        """
        Builds a short colored suffix comparing a weapon's damage to the
        currently equipped weapon, e.g. " (+2 im Vergleich zu Kurzschwert)".

        Args:
            weapon (Weapon): The weapon being offered/looked at.
            equipped (Weapon | None): The player's currently equipped weapon.

        Returns:
            str: Comparison suffix, or an empty string if nothing is equipped.
        """
        if equipped is None:
            return ""
        diff = weapon.damage - equipped.damage
        if diff > 0:
            return Fore.GREEN + f" | +{diff} ggü. {equipped.name}" + Style.RESET_ALL
        elif diff < 0:
            return Fore.RED + f" | {diff} ggü. {equipped.name}" + Style.RESET_ALL
        return f" | gleich wie {equipped.name}"

    def CompareArmor(self, armor: Armor, equipped: Armor | None) -> str:
        """
        Builds a short colored suffix comparing an armor's defense to the
        currently equipped armor, analogous to CompareWeapon.

        Args:
            armor (Armor): The armor being offered/looked at.
            equipped (Armor | None): The player's currently equipped armor.

        Returns:
            str: Comparison suffix, or an empty string if nothing is equipped.
        """
        if equipped is None:
            return ""
        diff = armor.defense - equipped.defense
        if diff > 0:
            return Fore.GREEN + f" | +{diff} ggü. {equipped.name}" + Style.RESET_ALL
        elif diff < 0:
            return Fore.RED + f" | {diff} ggü. {equipped.name}" + Style.RESET_ALL
        return f" | gleich wie {equipped.name}"

    def Trader(self, player, allItems: list, allWeapons: list = None, allArmor: list = None) -> None:
        """
        Handles a trader encounter.

        The player can buy up to three randomly selected items, one
        random weapon and one random armor piece, if they have enough gold.
        Buying a weapon or armor equips it immediately. The player can
        also sell items from their own inventory for half their value.

        Args:
            player (Player): The player instance.
            allItems (list[Item]): List of all possible items.
            allWeapons (list[Weapon]): List of all possible weapons.
            allArmor (list[Armor]): List of all possible armor pieces.
        """
        allWeapons = allWeapons or []
        allArmor = allArmor or []

        traderItems: list = []
        itemPool = [i for i in allItems if i.name != "--Ausverkauft--"]
        for _ in range(3): # Chooses 3 Items the trader offers
            candidate = random.choice(itemPool)
            traderItems.append(candidate.clone())

        traderWeapon = random.choice(allWeapons).clone() if allWeapons else None
        traderArmor = random.choice(allArmor).clone() if allArmor else None
        # Offers: [1-3] Items, [4] Weapon, [5] Armor, [6] Verlassen, [7] Item verkaufen
        soldWeapon = False
        soldArmor = False

        repeat = True
        clearConsole()
        while repeat:
            sleep(0.25)
            print(Fore.YELLOW + f"\n=== Trader ===")
            utils.slowPrint("Willkommen, Reisender...\n")

            for i, item in enumerate(traderItems, start=1):
                if item.name != "--Ausverkauft--":
                    print(f"[{i}]: {item.name} für {item.value} Gold")
                else:
                    print(f"[{i}]: {item.name}")

            if traderWeapon:
                if not soldWeapon:
                    compareText = self.CompareWeapon(traderWeapon, player.equippedWeapon)
                    print(f"[4]: {traderWeapon.name} (Waffe, +{traderWeapon.damage} Schaden{compareText}) für {traderWeapon.value} Gold")
                else:
                    print(f"[4]: --Ausverkauft--")

            if traderArmor:
                if not soldArmor:
                    compareText = self.CompareArmor(traderArmor, player.equippedArmor)
                    print(f"[5]: {traderArmor.name} (Rüstung, +{traderArmor.defense} Verteidigung{compareText}) für {traderArmor.value} Gold")
                else:
                    print(f"[5]: --Ausverkauft--")

            print(f"[6]: Verlassen")
            if player.items:
                print(f"[7]: Item verkaufen (halber Wert)")
            print(f"\nDu hast {Fore.YELLOW}{player.gold} Gold")

            choice = input("> ")
            if choice in {"1", "2", "3"}:
                idx = int(choice) - 1
                item = traderItems[idx]
                if item.name != "--Ausverkauft--":
                    if player.gold >= item.value:
                        player.gold -= item.value
                        player.items.append(item.clone())
                        item.name = "--Ausverkauft--"
                        item.value = 0
                        clearConsole()
                    else:
                        clearConsole()
                        print("Nicht genug Gold\n")
                        sleep(0.25)
                else:
                    clearConsole()
                    sleep(0.25)

            elif choice == "4" and traderWeapon:
                if not soldWeapon:
                    if player.gold >= traderWeapon.value:
                        player.gold -= traderWeapon.value
                        newWeapon = traderWeapon.clone()
                        if player.equippedWeapon is None:
                            player.EquipWeapon(newWeapon)
                        else:
                            player.AddWeaponToInventory(newWeapon)
                            print(f"\n{newWeapon.name} wurde deinem Inventar hinzugefügt!")
                        soldWeapon = True
                        sleep(1)
                        clearConsole()
                    else:
                        clearConsole()
                        print("Nicht genug Gold\n")
                        sleep(0.25)
                else:
                    clearConsole()
                    sleep(0.25)

            elif choice == "5" and traderArmor:
                if not soldArmor:
                    if player.gold >= traderArmor.value:
                        player.gold -= traderArmor.value
                        newArmor = traderArmor.clone()
                        if player.equippedArmor is None:
                            player.EquipArmor(newArmor)
                        else:
                            player.AddArmorToInventory(newArmor)
                            print(f"\n{newArmor.name} wurde deinem Inventar hinzugefügt!")
                        soldArmor = True
                        sleep(1)
                        clearConsole()
                    else:
                        clearConsole()
                        print("Nicht genug Gold\n")
                        sleep(0.25)
                else:
                    clearConsole()
                    sleep(0.25)

            elif choice == "6":
                repeat = False

            elif choice == "7" and player.items:
                clearConsole()
                print(Fore.YELLOW + "\nWelches Item möchtest du verkaufen?")
                for i, item in enumerate(player.items, start=1):
                    print(f" [{i}] {item.name} (Verkaufswert: {item.value // 2} Gold)")
                sellChoice = input("> ").strip()
                try:
                    sellIdx = int(sellChoice)
                    if not (1 <= sellIdx <= len(player.items)):
                        raise IndexError
                    player.SellItem(sellIdx - 1)
                    sleep(1)
                    clearConsole()
                except (ValueError, IndexError):
                    clearConsole()
                    print("Invalider Input! Bitte nochmal versuchen.\n")
                    sleep(0.25)

            else:
                clearConsole()
                print("Invalider Input! Bitte nochmal versuchen.\n")
                sleep(0.25)

    def SkillsOverview(self, player) -> None:
        """
        Shows the player's currently learned skills outside of combat.

        Purely informational (skills can only be used during combat).

        Args:
            player (Player): The player instance.
        """
        clearConsole()
        print(Fore.MAGENTA + Style.BRIGHT + "\n=== Deine Skills ===")
        print(Style.RESET_ALL + f"Energie: {player.energy}/{player.maxEnergy}\n")

        if not player.skills:
            print("Du hast noch keine Skills erlernt (Skills werden bei einem Level-Up freigeschaltet).")
        else:
            for i, s in enumerate(player.skills, start=1):
                effectLabel = {
                    "damage": "Schaden",
                    "damageAll": "Flächenschaden",
                    "heal": "Heilung",
                    "buff": "Buff",
                    "poison": "Vergiftung",
                    "shield": "Schild",
                }.get(s.effectType, s.effectType)
                print(f" [{i}] {Fore.YELLOW}{s.name}{Style.RESET_ALL} ({effectLabel}, Kosten: {s.cost})")
                print(f"     {s.description}")

        input("\nDrücke Enter um fortzufahren...")

    def EquipmentMenu(self, player) -> None:
        """
        Lets the player review and switch between owned weapons and
        armor pieces outside of combat (e.g. between encounters).

        Args:
            player (Player): The player instance.
        """
        repeat = True
        while repeat:
            clearConsole()
            print(Fore.CYAN + Style.BRIGHT + "\n=== Lager ===")
            print(Style.RESET_ALL + "Hier kannst du deine Ausrüstung wechseln.\n")

            # Aktuell ausgerüstete Gegenstände inkl. Werte
            if player.equippedWeapon:
                w = player.equippedWeapon
                critText = f", {w.critChance}% Krit" if w.critChance else ""
                print(f"Ausgerüstete Waffe:   {Fore.YELLOW}{w.name}{Style.RESET_ALL} (+{w.damage} Schaden{critText})")
            else:
                print(f"Ausgerüstete Waffe:   {Fore.YELLOW}Fäuste{Style.RESET_ALL} (+0 Schaden)")

            if player.equippedArmor:
                a = player.equippedArmor
                print(f"Ausgerüstete Rüstung: {Fore.YELLOW}{a.name}{Style.RESET_ALL} (+{a.defense} Verteidigung)")
            else:
                print(f"Ausgerüstete Rüstung: {Fore.YELLOW}Keine{Style.RESET_ALL} (+0 Verteidigung)")

            # Durchgehend nummerierte Liste aus Waffen- UND Rüstungsinventar
            options = [("weapon", idx, w) for idx, w in enumerate(player.weaponInventory)]
            options += [("armor", idx, a) for idx, a in enumerate(player.armorInventory)]

            print()
            if options:
                print("Im Inventar:")
                for i, (kind, _, obj) in enumerate(options, start=1):
                    if kind == "weapon":
                        critText = f", {obj.critChance}% Krit" if obj.critChance else ""
                        compareText = self.CompareWeapon(obj, player.equippedWeapon)
                        print(f" [{i}] {obj.name} (Waffe, +{obj.damage} Schaden{critText}, Verkaufswert: {obj.value} Gold{compareText})")
                    else:
                        compareText = self.CompareArmor(obj, player.equippedArmor)
                        print(f" [{i}] {obj.name} (Rüstung, +{obj.defense} Verteidigung, Verkaufswert: {obj.value} Gold{compareText})")
            else:
                print("Keine weiteren Gegenstände im Inventar.")

            backNumber = len(options) + 1
            print(f" [{backNumber}] Zurück")

            choice = input("> ").strip()
            try:
                choiceNum = int(choice)
            except ValueError:
                clearConsole()
                print("Invalider Input! Bitte nochmal versuchen.\n")
                sleep(1)
                continue

            if choiceNum == backNumber:
                repeat = False
            elif 1 <= choiceNum <= len(options):
                kind, idx, obj = options[choiceNum - 1]
                clearConsole()
                print(Fore.CYAN + f"\nWas möchtest du mit {obj.name} tun?")
                print(" [1] Ausrüsten")
                print(f" [2] Verkaufen (+{obj.value} Gold)")
                print(" [3] Zurück")
                subChoice = input("> ").strip()

                if subChoice == "1":
                    if kind == "weapon":
                        player.SwitchWeapon(idx)
                    else:
                        player.SwitchArmor(idx)
                    sleep(1)
                elif subChoice == "2":
                    if kind == "weapon":
                        player.SellWeapon(idx)
                    else:
                        player.SellArmor(idx)
                    sleep(1)
                elif subChoice == "3":
                    continue
                else:
                    clearConsole()
                    print("Invalider Input! Bitte nochmal versuchen.\n")
                    sleep(1)
            else:
                clearConsole()
                print("Invalider Input! Bitte nochmal versuchen.\n")
                sleep(1)
            
    @staticmethod
    def Scaling(enemies: list[Enemy], player) -> None:
        """
        Scales enemy stats based on player progress.

        Triggered after a certain number of completed encounters.

        Args:
            enemies (list[Enemy]): List of enemies.
            player (Player): The player instance.
        """
        if player.progress >= Encounter.SCALING_INTERVAL:
            for enemy in enemies:
                enemy.maxHp += round(enemy.baseHp / 2)
                enemy.hp = enemy.maxHp
                enemy.damage += round((enemy.baseDamage / 3) * 2)
            player.progress = 0
    
    @staticmethod
    def Boss(enemies: list[Enemy], player, encounter: "Encounter") -> bool:
        """
        Starts a boss fight encounter.

        Selects a random boss and runs combat until either
        the player or the boss is defeated.

        Args:
            enemies (list[Enemy]): List of all enemies.
            player (Player): The player instance.
            encounter (Encounter): The encounter handler.

        Returns:
            bool: True if the player defeated the boss, False if the
            player died during the fight. Progress/Highscore are only
            awarded by MainLoop when this returns True.
        """
        bossPool = [e for e in enemies if e.boss]
        pool = bossPool or enemies # Fallback, falls keine Bosse definiert sind
        boss = random.choice(pool).clone() # Pick a random boss
        bossList: list[Enemy] = [boss]
        clearConsole()

        print(Fore.RED + Style.BRIGHT)
        print("\n!!! Ein Boss erscheint !!!\n")
        sleep(1)
        print(f"Du begegnest: {boss.name.upper()}!")
        print(Style.RESET_ALL)

        fled = False
        while boss.hp > 0 and player.hp > 0:
            #print(f"{boss.name}: {boss.hp}/{boss.maxHp} HP")
            moveResult = encounter.PlayerMoveChoice(bossList, player)
            if moveResult == 1: # Spieler ist erfolgreich geflohen -> Kampf sofort beenden
                fled = True
                break
            encounter.TickStatusEffects(bossList, player)
            if player.hp <= 0: # Vergiftung kann den Spieler bereits hier töten
                break
            if boss.hp > 0:
                encounter.EnemyAttack(bossList, player)
            else:
                print(f"\nDu hast den Boss besiegt!")
                player.bossesDefeated += 1
                print(Fore.YELLOW + f"+{boss.gold} Gold")
                player.gold += boss.gold
                if not player.effect[1]: # Check if xp buff is active
                    player.levelProgress += boss.xp
                    print(Fore.GREEN + f"+{boss.xp} XP")
                else:
                    gained = 3 * boss.xp
                    player.levelProgress += gained
                    print(Fore.GREEN + f"Das Buch des Wissens hat sich ausgezahlt!\n+{gained} XP")
                sleep(1)
            
            levelUp = encounter.CheckForLevel(player.levelProgress, player.nextLevel)
            if levelUp:
                player = encounter.LevelUp(player)
                levelUp = False

        if fled:
            print(Fore.YELLOW + f"\nDu ziehst dich vom Kampf gegen {boss.name} zurück.")
            sleep(1)

        player.ResetCombatBuffs() # Temporäre Kampf-Buffs (z.B. Kriegsschrei) laufen aus
        player.CheckForEffect() # Temporäre Item-Effekte (z.B. Gift, Buch des Wissens) laufen aus

        return boss.hp <= 0 and player.hp > 0