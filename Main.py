from Encounter import Encounter
from Item import Item
from Weapon import Weapon
from Armor import Armor
from Entities.Enemy import Enemy
import os
import sys
import utils

clearConsole = utils.clearConsole

# ===== START OF GAME =====

allItems = Item.getAllItems()
allWeapons = Weapon.getAllWeapons()
allArmor = Armor.getAllArmor()

# Falls ein Spielstand existiert, kann er geladen werden, statt neu zu starten
loadedGame = False
if utils.SaveExists():
    clearConsole()
    print("=========================")
    print("        BODENLOS         ")
    print("=========================\n")
    print("Es wurde ein Spielstand gefunden.")
    print("[1] Spielstand laden")
    print("[2] Neues Spiel starten")
    startChoice = input("> ")

    if startChoice == "1":
        loaded = utils.LoadGame()
        if loaded:
            player, encounter, possibleEnemies = loaded
            loadedGame = True
        else:
            print("\nDer Spielstand konnte nicht geladen werden. Es wird ein neues Spiel gestartet.\n")

if not loadedGame:
    encounter = Encounter()
    player = encounter.PlayerCreator() # Function to create Player
    possibleEnemies = Enemy.getPossibleEnemies()

# ===== GAME =====

while True: 
    if player.hp <= 0: # Check if Player dead
        utils.DeleteSave() # Ein toter Charakter kann nicht weitergeladen werden
        break

    # Zwischen den Räumen: Hub-Menü (Weiterziehen, Lager, Items, Speichern)
    clearConsole()
    utils.showPlayer(player)

    actions = [("Weiterziehen", "advance")]
    if player.weaponInventory or player.armorInventory:
        actions.append(("Lager (Ausrüstung verwalten)", "storage"))
    if player.items:
        actions.append(("Items benutzen", "items"))
    if player.skills:
        actions.append(("Skills ansehen", "skills"))
    actions.append(("Erfolge ansehen", "achievements"))
    actions.append(("Speichern & Beenden", "save"))

    print()
    for i, (label, _) in enumerate(actions, start=1):
        print(f"[{i}] {label}")
    hubChoice = input("> ")

    try:
        hubIdx = int(hubChoice)
        if not (1 <= hubIdx <= len(actions)):
            raise IndexError
        action = actions[hubIdx - 1][1]
    except (ValueError, IndexError):
        action = "advance" # Bei ungültiger Eingabe einfach weiterziehen

    if action == "storage":
        encounter.EquipmentMenu(player)
        continue
    elif action == "skills":
        encounter.SkillsOverview(player)
        continue
    elif action == "achievements":
        utils.ShowAchievements(player)
        continue
    elif action == "items":
        player.items = player.RemoveUsedItem(player.items)
        continue
    elif action == "save":
        utils.SaveGame(player, encounter, possibleEnemies)
        clearConsole()
        print("Spielstand gespeichert. Bis zum nächsten Mal!")
        sys.exit(0)

    Encounter.MainLoop(player, encounter, possibleEnemies, allItems, allWeapons, allArmor)
    Encounter.Scaling(possibleEnemies, player)

    newAchievements = utils.CheckAchievements(player)
    if newAchievements:
        utils.AnnounceAchievements(newAchievements)
        input("\nDrücke Enter um fortzufahren...")

# ===== END OF GAME =====

clearConsole()
utils.gameOver(player)
