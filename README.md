# 🩸 Bloodline (Beta)

A small and minimalist **TUI** (Text-based User Interface) designed to track and analyze boss encounters in souls games.  
Record deaths and encounter times using global hotkeys and evaluate your performance statistically.

> [!IMPORTANT]
> ⚜️ **Seeker of Errors:** This project is currently in its *Beta-Phase*.  
> As with any treacherous journey, bugs may hide in the shadows. Your Feedback is a valuable soul - please share it!

---

## 📖 Table of Contents

- [🩸 Bloodline (Beta)](#-bloodline-beta)
  - [📖 Table of Contents](#-table-of-contents)
  - [💎 Key Features](#-key-features)
  - [📊 Workflow \& Analysis](#-workflow--analysis)
  - [💡 Good to Know](#-good-to-know)
    - [Version Check](#version-check)
    - [Font Selection](#font-selection)
  - [📥 Download](#-download)
    - [Releases](#releases)
    - [Preset \& Theme Templates](#preset--theme-templates)
  - [📟 Commands](#-commands)
    - [Syntax Legend](#syntax-legend)
    - [Command List](#command-list)
  - [⌨️ Default Keybinds](#️-default-keybinds)
  - [🔗 Dependencies](#-dependencies)
  - [🛡️ Compatibility \& Security](#️-compatibility--security)
  - [📜 License \& Usage](#-license--usage)

---

## 💎 Key Features

- **Console Experience:** Run exclusively through commands, featuring input history and auto-completion.

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

## 💡 Good to Know

### Version Check
Bloodline performs an automatic version check via the GitHub API on the program's startup, provided the last check was at least one hour ago. Depending on your internet connection and the API's response time, the startup may be delayed by a few seconds. To ensure a short startup process, the maximum wait time (timeout) is limited to 5s.

### Font Selection
> [!NOTE]
> The default theme uses the [DM Mono](https://fonts.google.com/specimen/DM+Mono) font. If this font is not installed, a warning will appear at startup. You can either install the font or use a custom [theme template](./templates/theme_template.json) to select a different font already available on your system.  
> **Tip:** Always use a *monospaced* font for the best visual experience.

---

## 📥 Download

### Releases
You can always find the latest versions on the [releases page](https://github.com/prjbl/bloodline/releases).

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
| Toplevel Commands | Description |
| :--- | :--- |
| `help` | Lists all command categories |
| `tracking` | Lists all tracking actions |
| `setup` | Lists all setup actions |
| `stats` | Lists all stats actions |
| `keybinds` | Lists all keybind actions |
| `settings` | Lists all settings actions |
| `quit` | Quits the application |

| Dynamic Commands | Description |
| :--- | :--- |
| `cancel` | Cancels the current input process. Only available during an active input request |

| Tracking Commands | Description |
| :--- | :--- |
| `tracking new` | Starts a new global tracking session |
| `tracking continue` | Continues an existing global tracking session |

| Setup Commands | Description |
| :--- | :--- |
| `setup add` | Adds a boss with the corresponding game to the save file |
| `setup identify boss` | Identifies an unknown boss and updates its meta info |
| `setup move boss` | Moves a boss to another game |
| `setup rename boss\|game` | Renames a boss / game |
| `setup delete boss\|game` | Deletes a boss / game |
| `setup import preset` | Imports and adds the game data to the save file (see [preset template](./templates/preset_template.json)) |

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
| `settings import theme` | Imports and changes the program's theme (see [theme template](./templates/theme_template.json)) |
| `settings preview theme` | Displays the current color theme |

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

---

## 🔗 Dependencies

Bloodline is *built with Python* and relies on the following external libraries:

| Library | Description of Use |
| :--- | :--- |
| [platformdirs](https://pypi.org/project/platformdirs/) | Provides system paths for local data |
| [pydantic](https://pypi.org/project/pydantic/) | Handles data validation for external files |
| [pynput](https://pypi.org/project/pynput/) | Manages global hotkey listeners |
| [requests](https://pypi.org/project/requests/) | Retrieves external api data |

To set up a development environment, install the required packages via the [requirements.txt](requirements.txt) file by running the following command in your terminal or powershell: `pip install -r requirements.txt`.

---

## 🛡️ Compatibility & Security

Bloodline has been tested with the anti-cheat software [Easy Anti-Cheat](https://www.easy.ac/) and [BattlEye](https://www.battleye.com/) without any issues. However, it remains possible that other anti-cheat solutions may flag the software.

Additionally, since the program utilizes global hotkeys via the pynput library, some antivirus programs may trigger a warning due to the nature of keyboard hooks.

---

## 📜 License & Usage

As this project is primarily intended to provide easy access for users and friends, no official open-source license is currently attached. Standard copyright law applies with the following express permissions:

- **Private Use:** You are free to use the [source code](./bloodline) and [releases](https://github.com/prjbl/bloodline/releases) for personal, non-commercial purposes.

- **Commercial Use:** Commercial use of the code or the resulting application is not permitted without prior written consent.