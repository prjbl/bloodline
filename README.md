# 🩸 Bloodline (Beta)

A small and minimalist **TUI** (Text-based User Interface) designed to track and analyze boss encounters in souls games.  
Record deaths and encounter times using global hotkeys and evaluate your performance statistically.

> ⚠️ <font color="#d4a61e">**State:** Beta-Phase</font>  
> <font color="#d4c392">This project is currently still in development. The core functions of the program are present, but errors and problems may still occur.  
> Constructive feedback is very welcome!</font>

---

## 📖 Table of Contents

- [🩸 Bloodline (Beta)](#-bloodline-beta)
  - [📖 Table of Contents](#-table-of-contents)
  - [💎 Key Features](#-key-features)
  - [📊 Workflow \& Analysis](#-workflow--analysis)
  - [📥 Download](#-download)
    - [Releases](#releases)
    - [Preset \& Theme Templates](#preset--theme-templates)
  - [📟 Commands](#-commands)
    - [Syntax Legend](#syntax-legend)
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

### Releases
You can always find the latest versions on the [releases page](https://github.com/.../bloodline/releases).

### Preset & Theme Templates
Examples for both the preset and theme files can be found in the [templates directory](./templates) of this repository.

---

## 📟 Commands

### Syntax Legend
| Symbol | Meaning |
| :--- | :--- |
| `\|` | Represents an "OR" choice |
| `[]` | Indicates an optional operator |
| `<>` | Acts as a placeholder for your specific input |

### Command List
| Toplevel Level Commands | Description |
| :--- | :--- |
| `help` | Lists all command categories |
| `tracking` | Lists all tracking actions |
| `setup` | Lists all setup actions |
| `stats` | Lists all stats actions |
| `keybinds` | Lists all keybind actions |
| `settings` | Lists all settings actions |
| `quit` | Quits the application |

| Tracking Commands | Description |
| :--- | :--- |
| `tracking new` | Starts a new gloabl tracking session |
| `tracking continue` | Continues an existing global tracking session |

| Setup Commands | Description |
| :--- | :--- |
| `setup add` | Adds a boss with the corresponding game to the save file |
| `setup identify boss` | Identifies an unknown boss and updates its meta infos |
| `setup move boss` | Moves a boss to another game |
| `setup rename boss\|game` | Renames a boss / game |
| `setup delete boss\|game` | Deletes a boss / game |
| `setup import preset` | Imports and adds the game data to the save file (see [templates](./templates)) |

| Stats Commands | Description |
| :--- | :--- |
| `stats list bosses [-a] [-s deaths\|time -o desc\|asc]` | Lists bosses by the selected filters. By default all bosses will be listed in the order they were added |
| `stats list games [-s deaths\|time -o desc\|asc]` | Lists all games by the selected filters. By default the games will be listed in the order they were added |
| `stats save` | Saves the tracking values to the selected boss in the save file |
| `stats export` | Exports all bosses with their corresponding values from the selected game to a .csv file |

| Keybind Commands | Description |
| :--- | :--- |
| `keybinds list` | Lists all hotkeys with their corresponding keybinds |
| `keybinds config <hotkey>` | Changes the keybind of the selected hotkey |

| Settings Commands | Description |
| :--- | :--- |
| `settings unlock\|lock overlay` | Enables / Disables the ability to move the overlay |
| `settings import theme` | Imports and changes the programs theme (see [templates](./templates)) |

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