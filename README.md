# 🩸 Bloodline

A small *TUI* (Text-based User Interface) designed to track and analyze boss encounters in games.  
Record deaths and elapsed time using global hotkeys and evaluate your performance statistically.

---

## 📖 Table of Contents

- [📥 Download](#-download)
- [🚀 Quick Start](#-quick-start)
- [💎 Key Features](#-key-features)
- [💡 Technical Notes](#-technical-notes)
- [📟 Commands](#-commands)
- [🐛 Submitting Issues](#-submitting-issues)
- [🛡️ Compatibility \& Security](#️-compatibility--security)
- [📜 License \& Usage](#-license--usage)

---

## 📥 Download

### Releases
You can always find the latest version on the [Releases](https://github.com/prjbl/bloodline/releases) page.

> [!IMPORTANT]
> Before your first startup, please make sure to check out the [💡 Technical Notes](#-technical-notes) and [🛡️ Compatibility \& Security](#️-compatibility--security) sections for important details regarding the program's behavior and limitations.

Bloodline is available for:

- 🖥 **Windows:** Standard Installer (`.exe`)

- 🐧 **Linux:**
  - **Debian-based:** Ubuntu, Mint, etc. (`.deb`)
  - **RHEL-based:** Fedora, CentOS, etc. (`.rpm`)
  - **Arch-based:** Manjaro, CachyOS, etc. (`.pkg.tar.zst`)

### Templates
Templates for game presets and custom themes are available for download in the [templates directory](./templates). Just adapt the values to fit your needs.

---

## 🚀 Quick Start

1. **Setup:** Import a game preset or manually create a new game and boss entry.
2. **Track:** Start the tracking session and log time and deaths as you play.
3. **Save:** Save the tracked data to your local save file.
4. **Analyze:** View your data listed and filtered according to your needs.

---

## 💎 Key Features

- **Console Experience:** Runs exclusively through commands, featuring input history and auto-completion.

- **Global Hotkey Tracking:** Document time and deaths while the game is running in the foreground.

- **Game Overlay:** Keep track of your stats live on top of the game.

- **Import & Export of Stats:** Import game presets as `.json` and export game data via `.csv` files.

- **Flexible Data Analysis:** Sort and display stored data using various filters.

- **Customizable Keybinds:** Select and assign keybinds for all tracking actions yourself.

- **Theme Support:** Adjust the program's appearance via `.json` theme files.

---

## 💡 Technical Notes

### User Directory
All exported files are stored in your system's *Documents* folder.

### Font Selection
Bloodline uses the [DM Mono](https://fonts.google.com/specimen/DM+Mono) font by default. If not installed, a warning will appear at startup. You can either install the font or use a custom font via the [theme template](./templates/theme_template.json).

> [!TIP]
> Always use a *monospaced* font for the best visual experience.

### Overlay Functionality
The overlay requires the game to run in *Windowed* or *Borderless Windowed* mode. For games running in *Fullscreen* mode, the game will render over the overlay.

### Keybinds Config
Hotkeys support both single keys and combinations using *Shift L* or *Shift R*. Since the combination accesses a key's shift value, this only works with keys that have a shift variant.

---

## 📟 Commands

All interactions within the application are handled through category-based commands. Some commands additionally feature a modular approach, allowing you to customize the results dynamically.

### Syntax Legend
| Symbol | Meaning |
| :--- | :--- |
| `\|` | Represents an "OR" choice |
| `[]` | Indicates an optional operator |
| `<>` | Acts as a placeholder for your specific input |

| Filter | Meaning |
| :--- | :--- |
| `-a` | Selects all bosses in the save file |
| `-s deaths\|time` | Sorts selected data by deaths / time |
| `-o desc\|asc` | Orders the sorted data descending / ascending |

### Canceling Actions
During an active input request, the `cancel` command can be used to abort the current process.

---

## 🐛 Submitting Issues

If you encounter any bug, crash, or strange behavior, please let me know! Just create a [New Issue](https://github.com/prjbl/bloodline/issues/new) with a brief summary of the problem and attach the affected log files.

### Log File Paths
- **Windows:** `%LOCALAPPDATA%\NME\Bloodline\logs`
- **Linux:** `~/.local/state/nme/bloodline/logs`

---

## 🛡️ Compatibility & Security

Testing Bloodline with the anti-cheat software [Easy Anti-Cheat](https://www.easy.ac/) and [BattlEye](https://www.battleye.com/) hasn't shown any issues. However, it remains possible that other anti-cheat solutions may flag the software.

Additionally, since the program utilizes global hotkeys, some antivirus programs may trigger a warning due to the nature of keyboard hooks.

---

## 📜 License & Usage

Bloodline is released under the [GNU General Public License v3.0](LICENSE).

You are free to use, modify and redistribute the code. However, any distributed modifications must be published under the same license.

The software is provided without any warranty.