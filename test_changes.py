"""
Kleines, nicht-interaktives Testskript um die geänderten Mechaniken
zu verifizieren, ohne das Spiel manuell durchspielen zu müssen.
"""
import random
from Entities.Player import Player
from Entities.Enemy import Enemy
from Encounter import Encounter
from Weapon import Weapon
from Armor import Armor
from Skill import Skill
import utils

def makePlayer():
    return Player(
        name="Testheld", hp=50, damage=10, level=3, gold=20,
        levelProgress=0, nextLevel=999999, progress=0, maxHp=50,
    )

def test_boss_win_awards_gold_and_xp_once():
    random.seed(1)
    player = makePlayer()
    boss = Enemy(xp=50, hp=1, name="Testboss", damage=1, level=1, gold=30, maxHp=1, effect=None, boss=True)
    startProgress = player.progress
    startGold = player.gold
    startXp = player.levelProgress
    # Angriff, der den Boss sofort tötet -> simulieren wir, indem wir PlayerMoveChoice patchen
    encounter = Encounter()
    def fakeMove(enemies, p):
        enemies[0].hp = 0 # Boss stirbt sofort
        return 0
    encounter.PlayerMoveChoice = fakeMove
    won = Encounter.Boss([boss], player, encounter)
    assert won is True, "Boss-Sieg sollte True zurückgeben"
    assert player.progress == startProgress, "Boss() selbst darf progress NICHT mehr erhöhen (das macht jetzt MainLoop)"
    assert player.gold == startGold + 30, f"Gold nicht korrekt vergeben: {player.gold}"
    assert player.levelProgress == startXp + 50, f"XP nicht korrekt vergeben: {player.levelProgress}"
    print("OK: Boss-Sieg vergibt Gold/XP genau einmal, progress bleibt Sache von MainLoop")

def test_boss_loss_gives_no_reward():
    random.seed(1)
    player = makePlayer()
    player.hp = 1
    boss = Enemy(xp=50, hp=9999, name="Testboss", damage=50, level=1, gold=30, maxHp=9999, effect=None, boss=True)
    encounter = Encounter()
    def fakeMove(enemies, p):
        return 0 # Spieler tut nichts Wirksames
    encounter.PlayerMoveChoice = fakeMove
    won = Encounter.Boss([boss], player, encounter)
    assert won is False, "Bei einer Niederlage muss False zurückgegeben werden"
    assert player.hp <= 0
    print("OK: Boss-Niederlage gibt False zurück (MainLoop vergibt dann keinen Fortschritt)")

def test_status_effects_player_poison_and_enemy_regen():
    random.seed(1)
    player = makePlayer()
    player.ApplyPoison(damage=5, turns=2)
    hydra = Enemy(xp=1, hp=10, name="Hydra", damage=1, level=1, gold=1, maxHp=30, effect="regen", boss=True)
    encounter = Encounter()
    startHp = player.hp
    startHydraHp = hydra.hp
    encounter.TickStatusEffects([hydra], player)
    assert player.hp == startHp - 5, f"Spieler-Vergiftung hat nicht (korrekt) zugeschlagen: {player.hp}"
    assert player.poisonTurns == 1
    assert hydra.hp > startHydraHp, "Hydra sollte durch 'regen' geheilt haben"
    print("OK: Spieler-Vergiftung und Gegner-Regeneration funktionieren")

def test_poison_cleared_after_combat():
    player = makePlayer()
    player.ApplyPoison(damage=5, turns=3)
    player.ResetCombatBuffs()
    assert player.poisonTurns == 0 and player.poisonDamage == 0
    print("OK: Vergiftung wird beim Kampfende zurückgesetzt (kein Übertrag in den nächsten Kampf)")

def test_steroide_gift_flag_no_longer_collide():
    from Item import Item
    player = makePlayer()
    import io, contextlib
    from unittest.mock import patch
    with contextlib.redirect_stdout(io.StringIO()):
        with patch('builtins.input', return_value=""):
            player.UseItem(Item("Steroide", 45))
    assert player.effect[0] is False, "Steroide darf effect[0] nicht mehr setzen"
    print("OK: Steroide setzt kein irreführendes Vergiftungs-Flag mehr")

def test_save_load_roundtrip_preserves_effects():
    player = makePlayer()
    player.effect = [True, True]
    encounter = Encounter()
    possibleEnemies = Enemy.getPossibleEnemies()
    utils.SaveGame(player, encounter, possibleEnemies)
    loaded = utils.LoadGame()
    assert loaded is not None
    loadedPlayer, _, _ = loaded
    assert loadedPlayer.effect == [True, True], "effect-Flags wurden beim Laden nicht wiederhergestellt"
    print("OK: Save/Load erhält effect-Flags")
    utils.DeleteSave()

def test_boss_flee_actually_ends_the_fight():
    random.seed(1)
    player = makePlayer()
    boss = Enemy(xp=50, hp=9999, name="Testboss", damage=50, level=1, gold=30, maxHp=9999, effect=None, boss=True)
    encounter = Encounter()
    startHp = player.hp
    def fakeMove(enemies, p):
        return 1 # Spieler flieht erfolgreich
    encounter.PlayerMoveChoice = fakeMove
    won = Encounter.Boss([boss], player, encounter)
    assert won is False, "Flucht ist kein Sieg, muss also False zurückgeben"
    assert player.hp == startHp, "Bei erfolgreicher Flucht darf der Boss nicht mehr zuschlagen können"
    print("OK: Flucht vor einem Boss beendet den Kampf sofort (kein Angriff mehr danach)")

def test_trap_room_type_is_classified_correctly():
    encounter = Encounter()
    assert encounter.ClassifyRoom(encounter.ROOM_CAMPFIRE_MAX + 1) == "Trap"
    assert encounter.ClassifyRoom(encounter.ROOM_TRAP_MAX) == "Trap"
    assert encounter.ClassifyRoom(encounter.ROOM_TRAP_MAX + 1) == "Trader"
    print("OK: Neuer Raumtyp 'Falle' wird korrekt zwischen Lagerfeuer und Trader eingeordnet")

def test_trap_only_applies_one_of_its_outcomes():
    import io, contextlib
    from unittest.mock import patch
    random.seed(2)
    player = makePlayer()
    encounter = Encounter()
    startGold = player.gold
    startHp = player.hp
    with contextlib.redirect_stdout(io.StringIO()):
        with patch('builtins.input', return_value=""):
            encounter.Trap(player)
    # Entweder Schaden ODER Goldverlust ODER gar kein Effekt - aber nicht beides gleichzeitig
    hpChanged = player.hp != startHp
    goldChanged = player.gold != startGold
    assert not (hpChanged and goldChanged), "Falle darf nicht gleichzeitig HP und Gold kosten"
    assert player.gold <= startGold, "Falle darf dem Spieler kein Gold schenken"
    assert player.hp <= startHp, "Falle darf den Spieler nicht heilen"
    print("OK: Falle wendet genau einen Effekt an (Schaden, Goldverlust oder Ausweichen)")

def test_stun_skips_players_turn():
    player = makePlayer()
    player.stunned = True
    encounter = Encounter()
    dummyEnemies = [Enemy(xp=1, hp=5, name="Dummy", damage=1, level=1, gold=1, maxHp=5, effect=None, boss=False)]
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        result = encounter.PlayerMoveChoice(dummyEnemies, player)
    assert result == 0, "Eine betäubte Runde ist keine Flucht, muss also 0 zurückgeben"
    assert player.stunned is False, "Betäubung muss nach der verpassten Runde aufgehoben werden"
    print("OK: Betäubung lässt genau eine Spielerrunde ausfallen und wird danach aufgehoben")

def test_shield_skill_reduces_incoming_damage():
    player = makePlayer()
    player.energy = player.maxEnergy
    eisenhaut = next(s for s in Skill.getAllSkills() if s.name == "Eisenhaut")
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        player.UseSkill(eisenhaut)
    assert abs(player.combatDamageReduction - 0.6) < 1e-9, f"Eisenhaut sollte den erlittenen Schaden um 40% senken: {player.combatDamageReduction}"

    enemy = Enemy(xp=1, hp=10, name="Testgegner", damage=10, level=1, gold=1, maxHp=10, effect=None, boss=False)
    encounter = Encounter()
    startHp = player.hp
    with contextlib.redirect_stdout(io.StringIO()):
        encounter.EnemyAttack([enemy], player)
    dmgTaken = startHp - player.hp
    assert dmgTaken == 6, f"10 Schaden * 0.6 (Schild) sollten 6 Schaden ergeben: {dmgTaken}"
    print("OK: Eisenhaut reduziert erlittenen Schaden wie erwartet")

def test_damage_all_skill_hits_every_enemy():
    player = makePlayer()
    player.energy = player.maxEnergy
    wirbelangriff = next(s for s in Skill.getAllSkills() if s.name == "Wirbelangriff")
    enemies = [
        Enemy(xp=1, hp=5, name="Gegner1", damage=1, level=1, gold=1, maxHp=5, effect=None, boss=False),
        Enemy(xp=1, hp=5, name="Gegner2", damage=1, level=1, gold=1, maxHp=5, effect=None, boss=False),
    ]
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        player.UseSkill(wirbelangriff, enemies)
    assert all(e.hp < 5 for e in enemies), "Wirbelangriff sollte allen übergebenen Gegnern Schaden zufügen"
    print("OK: Wirbelangriff trifft alle übergebenen Gegner gleichzeitig")

def test_sell_item_gives_half_value():
    from Item import Item
    player = makePlayer()
    player.items = [Item("Heiltrank", 20)]
    startGold = player.gold
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        refund = player.SellItem(0)
    assert refund == 10, f"Ein Item mit Wert 20 sollte für 10 Gold verkauft werden: {refund}"
    assert player.gold == startGold + 10
    assert player.items == []
    print("OK: Items werden beim Verkauf für den halben Wert vergütet")

def test_adrenalin_ampulle_cures_stun_and_poison():
    from Item import Item
    import io, contextlib
    from unittest.mock import patch
    player = makePlayer()
    player.ApplyPoison(damage=5, turns=2)
    player.stunned = True
    with contextlib.redirect_stdout(io.StringIO()):
        with patch('builtins.input', return_value=""):
            player.UseItem(Item("Adrenalin-Ampulle", 35))
    assert player.poisonTurns == 0 and player.stunned is False
    print("OK: Adrenalin-Ampulle heilt Vergiftung und Betäubung")

def test_achievements_unlock_once_and_persist_through_save_load():
    import os
    from Achievement import Achievement

    for f in (utils.SAVE_FILE, utils.ACHIEVEMENTS_FILE):
        if os.path.exists(f):
            os.remove(f)

    player = makePlayer()
    player.level = 2 # Erfüllt die Bedingung von "erste_schritte" (Level 2)

    newAchievements = utils.CheckAchievements(player)
    assert any(a.id == "erste_schritte" for a in newAchievements), "Level-Erfolg wurde nicht erkannt"

    # Ein bereits freigeschalteter Erfolg darf nicht doppelt vergeben werden
    newAchievements2 = utils.CheckAchievements(player)
    assert not any(a.id == "erste_schritte" for a in newAchievements2), "Erfolg wurde doppelt vergeben"

    # bossesDefeated muss über Save/Load erhalten bleiben, damit "Bossjäger" & Co. korrekt bleiben
    player.bossesDefeated = 1
    encounter = Encounter()
    possibleEnemies = Enemy.getPossibleEnemies()
    utils.SaveGame(player, encounter, possibleEnemies)
    loaded = utils.LoadGame()
    assert loaded is not None
    loadedPlayer, _, _ = loaded
    assert loadedPlayer.bossesDefeated == 1, "bossesDefeated wurde beim Laden nicht wiederhergestellt"

    utils.DeleteSave()
    if os.path.exists(utils.ACHIEVEMENTS_FILE):
        os.remove(utils.ACHIEVEMENTS_FILE)
    print("OK: Erfolge werden korrekt freigeschaltet, nicht doppelt vergeben, bossesDefeated übersteht Save/Load")

def test_weapon_armor_comparison_helpers():
    encounter = Encounter()
    weakSword = Weapon("Holzstock", damage=1, value=1)
    strongSword = Weapon("Excalibur", damage=10, value=1)
    text = encounter.CompareWeapon(strongSword, weakSword)
    assert "+9" in text
    text2 = encounter.CompareArmor(Armor("Stoffrobe", defense=1, value=1), Armor("Plattenpanzer", defense=6, value=1))
    assert "-5" in text2
    print("OK: Ausrüstungsvergleich-Helfer liefern plausible Werte")

if __name__ == "__main__":
    test_boss_win_awards_gold_and_xp_once()
    test_boss_loss_gives_no_reward()
    test_boss_flee_actually_ends_the_fight()
    test_trap_room_type_is_classified_correctly()
    test_trap_only_applies_one_of_its_outcomes()
    test_status_effects_player_poison_and_enemy_regen()
    test_poison_cleared_after_combat()
    test_stun_skips_players_turn()
    test_shield_skill_reduces_incoming_damage()
    test_damage_all_skill_hits_every_enemy()
    test_sell_item_gives_half_value()
    test_adrenalin_ampulle_cures_stun_and_poison()
    test_steroide_gift_flag_no_longer_collide()
    test_save_load_roundtrip_preserves_effects()
    test_weapon_armor_comparison_helpers()
    test_achievements_unlock_once_and_persist_through_save_load()
    print("\nAlle Tests erfolgreich.")
