# 🩸 Bloodline (Beta)

A small and minimalist **TUI** (Text-based User Interface) designed to track and analyze boss encounters in souls games.  
Record deaths and encounter times using global hotkeys and evaluate your performance statistically.

> [!IMPORTANT]
> ⚠️ **Seeker of Errors:** This project is currently in its *Beta-Phase*.  
> As with any treacherous journey, bugs may hide in the shadows. Your Feedback is a valuable soul - please share it!

---

## 📖 Table of Contents

- [💎 Key Features](#-key-features)
- [📊 Workflow & Analysis](#-workflow--analysis)
- [📥 Download](#-download)
- [💡 Technical Notes](#-technical-notes)
- [📟 Commands](#-commands)
- [⌨️ Default Keybinds](#️-default-keybinds)
- [🔗 Dependencies](#-dependencies)
- [🛡️ Compatibility & Security](#️-compatibility--security)
- [📜 License & Usage](#-license--usage)

---

## 💎 Key Features

- **Console Experience:** Runs exclusively through commands, featuring input history and auto-completion.

- **Global Hotkey Tracking:** Document time and deaths while the game is running in the foreground.

- **Import & Export of Stats:** Import game presets as `.json` and export game data via `.csv` files.

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
You can always find the latest versions on the [releases page](https://github.com/prjbl/bloodline/releases).  
Currently Bloodline is only available for **Windows** as a standalone file. Linux support is planned as a universal `.flatpak` package for the future.

### Preset & Theme Templates
Examples for both the preset and theme files can be found in the [templates directory](./templates) of this repository.

---

## 💡 Technical Notes

### Version Check
Bloodline performs an automatic version check via the GitHub API on the program's startup, provided the last check was at least one hour ago. Depending on your internet connection and the API's response time, the startup may be delayed by a few seconds. To ensure a short startup process, the maximum wait time (timeout) is limited to 5s.

### Font Selection
> [!NOTE]
> The default theme uses the [DM Mono](https://fonts.google.com/specimen/DM+Mono) font. If this font is not installed, a warning will appear at startup. You can either install the font or use a custom [theme template](./templates/theme_template.json) to select a different font already available on your system.  
> **Tip:** Always use a *monospaced* font for the best visual experience.

### Overlay Functionality
The functionality of the overlay is only guaranteed for games running in Windowed or Borderless Windowed mode. For games running in Fullscreen mode, the overlay will be overwritten by the game because it relies on a simple "topmost" function. This scenario occurs because the Graphics API takes control and prevents the DWM (Desktop Window Manager) from keeping windows on top.

### User Directory
All files exported by the program will be stored in the documents directory of the current user.

---

## 📟 Commands

Bloodline uses a nested command structure divided into categories. Besides the classic pattern, some commands feature a modular approach, allowing you to customize the results dynamically.

<details>
<summary><strong>Syntax Legend</strong></summary>

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

</details>

### General Pattern
All commands are built using the following pattern:

```
Category Action [-Scope-Filter arg1] [-Sort-Filter arg2 -Order-Filter arg3]
```

**Practical Example**  
To better understand the pattern, the following command is split into its individual parts to show each snippet's corresponding component:

| Category | Action | Scope | Sort | Order |
| :--- | :--- | :--- | :--- | :--- |
| `stats` | `list bosses` | `-a` | `-s deaths` | `-o asc` |

### Dynamic Commands
During an active input request, the `cancel` command can be used to abort the current process.

---

## ⌨️ Default Keybinds

Keybinds can be set using the `Shift L` / `Shift R` modifiers.

<details>
<summary><strong>Standard Hotkeys & Keybinds</strong></summary>

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

</details>

---

## 🔗 Dependencies

Bloodline is *built with Python 3.13* and relies on the following external libraries:

| Library | Description of Use |
| :--- | :--- |
| [platformdirs](https://pypi.org/project/platformdirs/) | Provides system paths for local data |
| [pydantic](https://pypi.org/project/pydantic/) | Handles data validation for external files |
| [pynput](https://pypi.org/project/pynput/) | Manages global hotkey listeners |
| [requests](https://pypi.org/project/requests/) | Retrieves external API data |

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