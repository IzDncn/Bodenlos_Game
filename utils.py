from colorama import Fore, Style, init
from time import sleep
import json
import os
init(autoreset=True)

def clearConsole() -> None:
    """
    Clears the console output.

    Uses 'cls' on Windows systems and 'clear' on Unix-based systems.
    """
    os.system("cls" if os.name == "nt" else "clear")

def printBox(text: str):
    width = len(text) + 4
    print(Fore.CYAN + "\n+" + "-" * width + "+")
    print(Fore.CYAN + f"|  {text}  |")
    print(Fore.CYAN + "+" + "-" * width + "+")

def slowPrint(text, delay=0.01):
    for char in text:
        print(char, end="", flush=True)
        sleep(delay)
    print()

def showPlayer(player):
    weaponName = player.equippedWeapon.name if player.equippedWeapon else "Fäuste"
    armorName = player.equippedArmor.name if player.equippedArmor else "Keine"
    totalDamage = player.damage + (player.equippedWeapon.damage if player.equippedWeapon else 0)

    print(Fore.GREEN + "\n=== Spieler ===")
    print(
        f"{player.name} | "
        f"Leben: {player.hp}/{player.maxHp} | "
        f"Schaden: {totalDamage} | "
        f"XP: {player.levelProgress}/{player.nextLevel} | "
        f"Gold: {Fore.YELLOW}{player.gold}"
    )
    print(
        Fore.GREEN +
        f"Waffe: {weaponName} | "
        f"Rüstung: {armorName} | "
        f"{Fore.MAGENTA}Energie: {player.energy}/{player.maxEnergy}"
    )

def gameOver(player):
    print("\n=========================")
    print(Fore.RED + Style.BRIGHT + "       Game Over         ")
    print("=========================")
    print(Style.RESET_ALL)
    print(f"Score: {Fore.YELLOW}{player.highScore}")
    showLeaderboard(updateLeaderboard(player))

# ===== Bestenliste =====

LEADERBOARD_FILE = "leaderboard.json"

def loadLeaderboard() -> list:
    """
    Loads the persistent leaderboard from disk.

    Returns:
        list: List of {"name": str, "score": int} entries, or an empty
        list if no leaderboard file exists or it is unreadable.
    """
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def updateLeaderboard(player, topN: int = 10) -> list:
    """
    Adds the current run's score to the persistent leaderboard, keeping
    only the top entries, and saves it back to disk.

    Args:
        player (Player): The player instance whose run just ended.
        topN (int): How many entries to keep.

    Returns:
        list: The updated, sorted leaderboard.
    """
    board = loadLeaderboard()
    board.append({"name": player.name, "score": player.highScore})
    board.sort(key=lambda entry: entry["score"], reverse=True)
    board = board[:topN]

    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(board, f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # Bestenliste ist ein Bonus-Feature, ein Schreibfehler soll den Game-Over-Screen nicht crashen

    return board

def showLeaderboard(board: list) -> None:
    """
    Prints the persistent leaderboard.

    Args:
        board (list): List of {"name": str, "score": int} entries.
    """
    print(Fore.CYAN + Style.BRIGHT + "\n=== Bestenliste ===")
    print(Style.RESET_ALL, end="")
    for i, entry in enumerate(board, start=1):
        print(f" {i}. {entry['name']:<15} {Fore.YELLOW}{entry['score']}")

# ===== Erfolge =====

ACHIEVEMENTS_FILE = "achievements.json"

def LoadUnlockedAchievements() -> set:
    """
    Loads the set of already unlocked achievement IDs from disk.

    Anders als der Spielstand gilt achievements.json über mehrere Runs
    hinweg - einmal freigeschaltete Erfolge bleiben also auch nach
    einem Game Over oder einem neuen Spiel erhalten.

    Returns:
        set: IDs der bereits freigeschalteten Erfolge, leer falls
        noch keine Datei existiert oder sie unlesbar ist.
    """
    if not os.path.exists(ACHIEVEMENTS_FILE):
        return set()
    try:
        with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (json.JSONDecodeError, OSError):
        return set()

def SaveUnlockedAchievements(unlockedIds: set) -> None:
    """
    Persists the set of unlocked achievement IDs to disk.

    Args:
        unlockedIds (set): IDs aller bisher freigeschalteten Erfolge.
    """
    try:
        with open(ACHIEVEMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(unlockedIds), f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # Erfolge sind ein Bonus-Feature, ein Schreibfehler soll das Spiel nicht crashen

def CheckAchievements(player) -> list:
    """
    Checks all achievements against the player's current stats and
    unlocks any that haven't been unlocked yet.

    Should be called regularly (z.B. nach jedem abgeschlossenen
    Encounter), damit neue Erfolge zeitnah erkannt werden.

    Args:
        player (Player): The current player instance.

    Returns:
        list[Achievement]: Erfolge, die durch diesen Aufruf neu
        freigeschaltet wurden (leer, falls keine neuen dazukamen).
    """
    from Achievement import Achievement  # Lokaler Import, um zirkuläre Importe zu vermeiden

    unlockedIds = LoadUnlockedAchievements()
    newlyUnlocked = []

    for achievement in Achievement.getAllAchievements():
        if achievement.id not in unlockedIds and achievement.IsUnlocked(player):
            unlockedIds.add(achievement.id)
            newlyUnlocked.append(achievement)

    if newlyUnlocked:
        SaveUnlockedAchievements(unlockedIds)

    return newlyUnlocked

def AnnounceAchievements(newlyUnlocked: list) -> None:
    """
    Prints a short announcement for each newly unlocked achievement.

    Args:
        newlyUnlocked (list[Achievement]): Result of CheckAchievements.
    """
    for achievement in newlyUnlocked:
        print(Fore.MAGENTA + Style.BRIGHT + f"\n★ Erfolg freigeschaltet: {achievement.name}")
        print(Style.RESET_ALL + f"  {achievement.description}")
        sleep(1)

def ShowAchievements(player) -> None:
    """
    Displays every achievement in the game, marking which ones are
    already unlocked.

    Args:
        player (Player): The current player instance.
    """
    from Achievement import Achievement  # Lokaler Import, um zirkuläre Importe zu vermeiden

    unlockedIds = LoadUnlockedAchievements()
    clearConsole()
    print(Fore.MAGENTA + Style.BRIGHT + "\n=== Erfolge ===")
    print(Style.RESET_ALL, end="")

    for achievement in Achievement.getAllAchievements():
        if achievement.id in unlockedIds:
            print(Fore.GREEN + f" [X] {achievement.name}{Style.RESET_ALL} - {achievement.description}")
        else:
            print(Fore.RED + f" [ ] {achievement.name}{Style.RESET_ALL} - {achievement.description}")

    input("\nDrücke Enter um fortzufahren...")

# ===== Speicherstand =====

SAVE_FILE = "savegame.json"

def SaveExists() -> bool:
    """
    Checks whether a save file already exists on disk.

    Returns:
        bool: True if a save file was found, otherwise False.
    """
    return os.path.exists(SAVE_FILE)

def DeleteSave() -> None:
    """
    Deletes the current save file, if one exists.

    Called when a run ends (the player died), so a dead character
    can't be reloaded.
    """
    if SaveExists():
        os.remove(SAVE_FILE)

def SaveGame(player, encounter, possibleEnemies) -> None:
    """
    Saves the current game state to disk as JSON.

    Equipment, items and skills are stored by name only. Their full
    definitions are looked up again from the master lists on load,
    so the save file stays small and always matches the current game data.

    Args:
        player (Player): The current player instance.
        encounter (Encounter): The current encounter handler.
        possibleEnemies (list[Enemy]): The (possibly scaled) enemy pool.
    """
    data = {
        "player": {
            "name": player.name,
            "hp": player.hp,
            "maxHp": player.maxHp,
            "damage": player.damage,
            "level": player.level,
            "gold": player.gold,
            "levelProgress": player.levelProgress,
            "nextLevel": player.nextLevel,
            "progress": player.progress,
            "highScore": player.highScore,
            "maxEnergy": player.maxEnergy,
            "energy": player.energy,
            "equippedWeapon": player.equippedWeapon.name if player.equippedWeapon else None,
            "equippedArmor": player.equippedArmor.name if player.equippedArmor else None,
            "weaponInventory": [w.name for w in player.weaponInventory],
            "armorInventory": [a.name for a in player.armorInventory],
            "items": [i.name for i in player.items],
            "skills": [s.name for s in player.skills],
            "effect": player.effect,
            "bossesDefeated": player.bossesDefeated,
        },
        "encounter": {
            "lastRoomType": encounter.lastRoomType,
        },
        "enemies": [
            {"name": e.name, "hp": e.hp, "maxHp": e.maxHp, "damage": e.damage}
            for e in possibleEnemies
        ],
    }

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def LoadGame():
    """
    Loads a previously saved game state from disk.

    Reconstructs the player, encounter and enemy pool. Equipment, items
    and skills are looked up by name in the master lists, so their stats
    always match the current game data instead of a possibly outdated copy.

    Returns:
        tuple[Player, Encounter, list[Enemy]] | None: The restored state,
        or None if no valid save file exists.
    """
    if not SaveExists():
        return None

    # Lokale Imports, um zirkuläre Importe mit Encounter/Player zu vermeiden
    from Entities.Player import Player
    from Entities.Enemy import Enemy
    from Encounter import Encounter
    from Weapon import Weapon
    from Armor import Armor
    from Item import Item
    from Skill import Skill

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        allWeapons = Weapon.getAllWeapons()
        allArmor = Armor.getAllArmor()
        allItems = Item.getAllItems()
        allSkills = Skill.getAllSkills()

        def findWeapon(name):
            return next((w.clone() for w in allWeapons if w.name == name), None)

        def findArmor(name):
            return next((a.clone() for a in allArmor if a.name == name), None)

        def findItem(name):
            return next((i.clone() for i in allItems if i.name == name), None)

        def findSkill(name):
            return next((s for s in allSkills if s.name == name), None)

        p = data["player"]
        player = Player(
            name=p["name"],
            hp=p["hp"],
            damage=p["damage"],
            level=p["level"],
            gold=p["gold"],
            levelProgress=p["levelProgress"],
            nextLevel=p["nextLevel"],
            progress=p["progress"],
            maxHp=p["maxHp"],
        )
        player.highScore = p["highScore"]
        player.maxEnergy = p["maxEnergy"]
        player.energy = p["energy"]

        if p["equippedWeapon"]:
            player.equippedWeapon = findWeapon(p["equippedWeapon"])
        if p["equippedArmor"]:
            player.equippedArmor = findArmor(p["equippedArmor"])

        player.weaponInventory = [w for w in (findWeapon(n) for n in p["weaponInventory"]) if w]
        player.armorInventory = [a for a in (findArmor(n) for n in p["armorInventory"]) if a]
        player.items = [i for i in (findItem(n) for n in p["items"]) if i]
        player.skills = [s for s in (findSkill(n) for n in p["skills"]) if s]
        player.effect = p.get("effect", [False, False]) # Fallback für Spielstände vor diesem Feature
        player.bossesDefeated = p.get("bossesDefeated", 0) # Fallback für Spielstände vor diesem Feature

        encounter = Encounter()
        encounter.lastRoomType = data["encounter"]["lastRoomType"]

        # Skalierte Werte der Gegner-Vorlagen wiederherstellen (siehe Encounter.Scaling)
        possibleEnemies = Enemy.getPossibleEnemies()
        savedEnemies = {e["name"]: e for e in data["enemies"]}
        for enemy in possibleEnemies:
            saved = savedEnemies.get(enemy.name)
            if saved:
                enemy.hp = saved["hp"]
                enemy.maxHp = saved["maxHp"]
                enemy.damage = saved["damage"]

        return player, encounter, possibleEnemies
    except (KeyError, ValueError, OSError):
        # Beschädigter Spielstand -> lieber neu starten als abstürzen
        return None