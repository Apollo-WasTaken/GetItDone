# GetItDone

![Logo](assets/logo.png)

## Overview
GetItDone is a sleek, custom‑tkinter based task manager that helps you track, edit, and delete your to‑do items. It uses the **Anthropic Sans** font family for a modern look and a Midnight Indigo theme.

## Screenshots

![Main UI](assets/screenshot_main.png)

![Edit Task Dialog](assets/screenshot_edit.png)

## Features
- Add, edit, and delete tasks
- Persistent storage in `tasks.json`
- Custom fonts loaded process‑private on Windows
- Responsive layout that fits an 800×600 window
- Clean, commented codebase

## Installation
```bash
# Clone the repository (if not already)
git clone <repo-url>
cd GetItDone

# (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

The application window will appear with the custom theme and fonts applied.
## Building the executable

You can package the app as a Windows executable using PyInstaller:

```bash
python -m pip install -r requirements.txt  # ensures PyInstaller is installed
python -m PyInstaller --onefile --windowed --icon get_it_done_logo.ico --name GetItDone main.py
```

The resulting `GetItDone.exe` will be placed in the `dist` folder.

## Contributing
Feel free to open issues or submit pull requests. Keep the code style consistent and update documentation when adding features.

## License
This project is licensed under the MIT License.