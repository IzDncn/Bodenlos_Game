# BODENLOS

A text-based dungeon crawler for the terminal. Fight through an endless series of randomly generated rooms, collect loot, learn skills, and see how far you get before you fall.

*Bodenlos* is German for "bottomless". The game is written in Python, and all in-game text (menus, item names, enemies) is in German.

## Features

- Six room types: fights, chests, campfires, traps, traders and bosses
- Turn-based combat with items, skills, an energy system, crits, poison, stun and more
- Leveling with a new skill to choose on every level-up (10 skills in total)
- Weapons and armor with an equipment menu, comparisons and selling
- Enemies that grow stronger the longer you survive
- Save & load (one slot, permadeath), a top-10 leaderboard and 10 persistent achievements

## Requirements

- Python 3.9 or newer
- [colorama](https://pypi.org/project/colorama/) (colored terminal output)

## Installation & Running

Download or clone the project, open a terminal in the project folder and run:

```bash
pip install colorama
python Main.py
```

> **Note:** Always start the game from the project folder. Save files are written to the current working directory.

## How to Play

All menus work by typing the number of an option and pressing **Enter**.

1. If a save file exists, you can load it or start a new game.
2. Enter your name. You start with **20 HP, 3 damage, 10 gold, 10 energy** and no equipment.
3. Between rooms you land in the **hub menu**:

| Option | Description |
|--------|-------------|
| Weiterziehen | Enter the next random room |
| Lager | Manage weapons and armor (only shown if you carry spare equipment) |
| Items benutzen | Use an item outside of combat (only shown if you own items) |
| Skills ansehen | View your learned skills (only shown once you have learned one) |
| Erfolge ansehen | View all achievements |
| Speichern & Beenden | Save the game and quit |

The game ends when your HP reaches 0. Your **score** is the number of fights won + chests opened + trader visits + bosses defeated. Campfires, traps and fleeing do not count.

## Rooms

| Room | What happens |
|------|--------------|
| **Fight** | A group of enemies attacks: 1–4 at first, up to 2–6 later on (see [Combat](#combat)) |
| **Chest** | 5–100 gold and 2–40 XP. 15% chance for a bonus weapon, 15% for a bonus armor piece |
| **Campfire** | Restores 50% of your missing HP and refills your energy |
| **Trap** | 20% you dodge it, 45% arrow volley (15% of max HP, reduced by armor), 35% a thief steals 5–25 gold |
| **Trader** | Sells 3 random items, 1 weapon and 1 armor piece. You can sell your items for half their price |
| **Boss** | A single, powerful enemy with big rewards |

Early on (score 0–1) you mostly meet fights and chests, and traders are very rare. From score 2, traders become common; from score 5, bosses can appear (about 10% of rooms). Chests, campfires, traps, traders and bosses never appear twice in a row.

## Combat

Each round you pick one action:

| Action | Description |
|--------|-------------|
| **[1] Angreifen** | Attack a chosen enemy. Damage = base damage + weapon bonus. Weapons have a crit chance for double damage |
| **[2] Item benutzen** | Use an item from your inventory |
| **[3] Skill benutzen** | Use a learned skill (costs energy) |
| **[4] Wegrennen** | Try to flee. Chance: 81% vs. 1 enemy, 61% vs. 2, 41% vs. 3, 21% vs. 4+ enemies and 21% vs. bosses |

Every valid action uses up your turn. Afterwards **one random living enemy** attacks you. Armor subtracts its defense value from every hit (minimum 1 damage).

- **Energy:** you regain 2 energy per round (max 10, +1 per level). Campfires and level-ups refill it completely.
- **Poison:** ticks every round for 3 rounds. Can hit you (Giftfrosch) or enemies (Giftpfeil skill).
- **Stun:** you skip your next turn.
- **Cleanup:** poison, stun and temporary combat buffs end when the fight ends.
- **Rewards:** every kill gives gold and XP. Fleeing gives nothing and does not raise your score.

## Progression

**Leveling:** you need 30 XP for level 2, and every further level requires 20 more XP than the last (50, 70, ...). XP resets to 0 on level-up. Each level-up gives:

- +5 max HP (fully healed) and +1 damage
- +1 max energy (fully refilled)
- A new skill: pick 1 of 2 random skills you haven't learned yet

**Enemy scaling:** after every 8 finished rooms, all enemies permanently gain +50% of their base HP and +2/3 of their base damage.

## Game Reference

### Items

Items can be bought from traders and used in the hub menu or during combat.

| Name | Price | Effect |
|------|------:|--------|
| Heiltrank | 20 | Restores 25% of your max HP |
| Steroide | 45 | +50% base damage (permanent) |
| Gift | 1 | −1 damage, −5 HP and −5 max HP (permanent) |
| Rüstung | 40 | +25% max HP (permanent). Not the same as armor pieces below |
| Buch des Wissens | 50 | Triples the XP you get from kills until the end of your next fight |
| Geheimnisvolles Artefakt | 75 | 50/50: max HP, HP and damage all +2, or all −1 |
| Fokus-Trank | 30 | Refills your energy completely |
| Adrenalin-Ampulle | 35 | Cures poison and stun |

### Weapons & Armor

Weapons add bonus damage and may crit for double damage. Armor reduces the damage of every hit you take by a flat amount. Buying or finding equipment puts it into your inventory, or equips it right away if that slot is empty. Use the **Lager** in the hub menu to switch, compare and sell equipment (sold for the listed value).

| Weapon | Damage | Crit | Value |
|--------|-------:|-----:|------:|
| Rostiger Dolch | +1 | 15% | 15 |
| Kurzschwert | +3 | 5% | 35 |
| Assassinendolch | +2 | 35% | 45 |
| Elfenbogen | +4 | 25% | 55 |
| Kriegshammer | +6 | 0% | 70 |
| Kriegssense | +8 | 8% | 120 |
| Excalibur | +10 | 10% | 150 |
| Kriegsaxt der Titanen | +12 | 5% | 180 |

| Armor | Defense | Value |
|-------|--------:|------:|
| Stoffrobe | 1 | 20 |
| Lederrüstung | 2 | 40 |
| Schattenmantel | 3 | 70 |
| Kettenhemd | 4 | 65 |
| Wächterschild-Rüstung | 5 | 90 |
| Plattenpanzer | 6 | 100 |
| Obsidianrüstung | 7 | 130 |
| Drachenschuppenrüstung | 9 | 160 |

### Skills

Skills cost energy and can only be used in combat. Damage skills scale with your base damage + weapon bonus (no crits).

| Skill | Cost | Effect |
|-------|-----:|--------|
| Wuchtschlag | 4 | 2× damage to one enemy |
| Meditation | 3 | Heal 20% of max HP |
| Kriegsschrei | 5 | +50% damage for the rest of the fight |
| Präziser Stich | 6 | 3× damage to one enemy |
| Zweiter Atem | 7 | Heal 40% of max HP |
| Adrenalinschub | 8 | 2.5× damage to one enemy |
| Eisenwille | 9 | Heal 30% of max HP |
| Giftpfeil | 5 | Poisons one enemy for 3 rounds (your level + 1 damage per round) |
| Wirbelangriff | 6 | 1.2× damage to all enemies |
| Eisenhaut | 6 | −40% damage taken for the rest of the fight |

### Enemies

| Enemy | HP | Damage | XP | Gold | Special |
|-------|---:|-------:|---:|-----:|---------|
| Kobold | 1 | 2 | 1 | 4 | |
| Skelett | 2 | 3 | 3 | 3 | |
| Zombie | 3 | 2 | 4 | 3 | |
| Magier | 2 | 4 | 8 | 1 | |
| Golem | 5 | 1 | 7 | 5 | |
| Drache | 7 | 5 | 15 | 10 | |
| Wolfsrudel | 4 | 4 | 6 | 6 | |
| Ork-Krieger | 6 | 5 | 10 | 8 | |
| Ghul | 5 | 4 | 9 | 7 | |
| Grottenwächter | 4 | 3 | 7 | 6 | 35% chance to stun you |

**Bosses**

| Boss | HP | Damage | XP | Gold | Special |
|------|---:|-------:|---:|-----:|---------|
| Feuerriese | 20 | 6 | 50 | 30 | |
| Hydra | 30 | 4 | 50 | 30 | Regenerates 10% max HP per round |
| Giftfrosch | 12 | 10 | 50 | 30 | 40% chance to poison you |
| Oger | 45 | 7 | 50 | 30 | |
| Lichkönig | 25 | 8 | 55 | 35 | Heals itself for half the damage it deals |
| Frostkoloss | 28 | 6 | 55 | 32 | 35% chance to stun you |

*Values shown are the base stats before scaling.*

### Achievements

Unlocked achievements are remembered across runs.

| Category | Achievements |
|----------|--------------|
| Level | Erste Schritte (level 2), Veteran (level 5), Legende (level 10) |
| Gold | Wohlhabend (100 gold at once), Steinreich (300 gold at once) |
| Score | Entdecker (score 10), Weitgereist (score 25) |
| Bosses | Bossjäger (1 boss), Bosstöter (3 bosses) |
| Skills | Gelehrter (learn 3 skills) |

## Save Files

All files are created in the folder you start the game from. Delete a file to reset it.

| File | Purpose |
|------|---------|
| `savegame.json` | Your current run. Created via **Speichern & Beenden** in the hub menu (saving during a fight is not possible) |
| `leaderboard.json` | Top 10 scores, updated when a run ends |
| `achievements.json` | Unlocked achievements, kept across runs |

There is only **one save slot** and death is permanent: when your character dies, `savegame.json` is deleted. This also happens if you started a *new* game while an old save existed.

## Project Structure

```
.
├── Main.py            # Entry point: start menu, hub menu, main loop
├── Encounter.py       # Rooms, combat, trader, leveling, enemy scaling
├── Item.py            # Consumable items
├── Weapon.py          # Weapons
├── Armor.py           # Armor pieces
├── Skill.py           # Skills
├── Achievement.py     # Achievements
├── utils.py           # Console helpers, save/load, leaderboard, achievement storage
├── test_changes.py    # Non-interactive tests
└── Entities/
    ├── Entity.py      # Base class (HP, damage, poison)
    ├── Player.py      # Player: inventory, equipment, skills, item effects
    └── Enemy.py       # Enemy definitions
```

## Extending the Game

| To add... | Do this |
|-----------|---------|
| Enemy / boss | Add an `Enemy(...)` to `Enemy.getPossibleEnemies()`. Set `boss=True` for bosses. Supported `effect` values: `stun`, `poison`, `drain`, `regen` |
| Item | Add it to `Item.getAllItems()` and implement its effect by name in `Player.UseItem()` |
| Weapon / armor | Add it to `Weapon.getAllWeapons()` / `Armor.getAllArmor()` |
| Skill | Add it to `Skill.getAllSkills()`. Existing `effectType`s: `damage`, `damageAll`, `heal`, `poison`, `buff`, `shield`. New types need handling in `Player.UseSkill()` and `Encounter.PlayerMoveChoice()` |
| Achievement | Add it to `Achievement.getAllAchievements()` with a unique, stable `id`. Supported `statKey`s: `level`, `gold`, `highScore`, `bossesDefeated`, `skills` |

Equipment, items, skills and enemies are stored **by name** in the save file. Renaming or removing an entry means old saves will silently lose it.

## Tests

```bash
python test_changes.py
```

> **Warning:** the tests create and delete `savegame.json` and `achievements.json` in the current folder. Run them from a copy of the project, or make sure you have nothing you want to keep in those files.
