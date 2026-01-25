# 🩸 Bloodline (Beta)

A small and minimalist **TUI** (Text-based User Interface) designed to track and analyze boss encounters in souls games.  
Record deaths and encounter times using global hotkeys and evaluate your performance statistically.

> ⚠️ **State:** Beta-Phase  
> This project is currently still in development. The core functions of the program are present, but errors and problems may still occur.  
> Constructive feedback is very welcome!

---

## 📖 Table of Contents

- [🩸 Bloodline (Beta)](#-bloodline-beta)
  - [📖 Table of Contents](#-table-of-contents)
  - [💎 Key Features](#-key-features)
  - [📊 Workflow \& Analysis](#-workflow--analysis)
  - [📥 Download](#-download)
  - [📟 Commands](#-commands)
    - [Syntax Guide](#syntax-guide)
    - [Command List](#command-list)
  - [⌨️ Default Keybinds](#️-default-keybinds)

---

## 💎 Key Features

- **Console Experience:** Operations run exclusively through command input.
- **Global Hotkey Tracking:** Document time and deaths while the game is running in the foreground.
- **Local Data Management:** All data is stored in a local database.
- **Import & Export of Stats:** Import game presets as `.json` and export game data via `.csv` files
- **Flexible Data Analysis:** Sort and display stored data using various filters.
- **Customizable Keybinds:** Select and assign keybinds for all tracking actions yourself.
- **Theme Support:** Adjust the program's appearance via `.json` theme files.

---

## 📊 Workflow & Analysis

The program allows you to precisely evaluate your stored data. A typical workflow could look as follows:

1. **Setup:** Add a specific boss and game to your local save file.
2. **Track:** Monitor time and deaths during a fight.
3. **Save:** Save the tracked data to your save file.
4. **Analyze:** View your data listed and filtered according to your needs.

---

## 📥 Download

You can always find the latest versions on the [Releases page](https://github.com/.../bloodline/releases) of this repo.

---

## 📟 Commands

### Syntax Guide
| Symbol | Meaning |
| :--- | :--- |
| `\|` | Represents an "OR" choice |
| `[]` | Indicates an optional operator |
| `<>` | Acts as a placeholder for your specific input |

### Command List
- `help`: Lists all command categories
- `tracking`: Lists all tracking commands
  - `tracking new`: Starts a new gloabl tracking session
  - `tracking continue`: Continues an existing global tracking session
- `setup`: Lists all setup commands
  - `setup add`: Adds a boss with the corresponding game to the save file
  - `setup identify boss`: Identifies an unknown boss and updates its meta infos
  - `setup move boss`: Moves a boss to another game
  - `setup rename boss|game`: Renames a boss / game
  - `setup delete boss|game`: Deletes a boss / game
  - `setup import preset`: Imports and adds the game data to the save file
- `stats`: Lists all stats commands
  - `stats list bosses [-a] [-s deaths|time -o desc|asc]`: Lists bosses by the selected filters. By default all bosses will be listed in the order they were added
  - `stats list games [-s deaths|time -o desc|asc]`: Lists all games by the selected filters. By default the games will be listed in the order they were added
  - `stats save`: Saves the tracking values to the selected boss in the save file
  - `stats export`: Exports all bosses with their corresponding values from the selected game to a .csv file
- `keybinds`: Lists all keybind commands
  - `keybinds list`: Lists all hotkeys with their corresponding keybinds
  - `keybinds config <hotkey>`: Changes the keybind of the selected hotkey
- `settings`: Lists all settings commands
  - `settings unlock|lock overlay`: Enables / Disables the ability to move the overlay
  - `settings import theme`: Imports and changes the programs theme
- `quit`: Quits the application

---

## ⌨️ Default Keybinds

Keybinds can be set using the `Shift L` / `Shift R` modifiers.

| Action | Keybind |
| :--- | :--- |
| **Counter Increase** | `+` |
| **Counter Decrease** | `-` |
| **Counter Reset** | `/` |
| **Timer Start** | `)` / `Shift` + `9` |
| **Timer Pause & Resume** | `=` / `Shift` + `0` |
| **Timer Stop** | `?` / `Shift` + `ß` |
| **Timer Reset** | `*` / `Shift` + `+` |
| **Key Listener End** | `°` / `Shift` + `^` |