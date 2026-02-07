# SDAW (Smart Desktop Assistant for Windows)

A modern, Python-based desktop assistant with voice and text capabilities.

## Features

- **Dual Input Modes**: Seamlessly switch between or use both Voice and Text commands.
- **Offline Mode**: Automatically detects internet connectivity and switches to a "Text Only" mode if offline.
- **Modern UI**: Built with `CustomTkinter` for a sleek, dark-themed interface.
- **Visual Feedback**: Real-time status updates and animated avatar background.
- **Multi-functionality**:
    - Launch Windows apps (Notepad, Calculator, Paint, etc.)
    - Search Google, Wikipedia, and YouTube.
    - Play videos directly.
    - Query WolframAlpha for general knowledge.
    - System controls (Shutdown).

## Requirements

- Python 3.10+
- See `requirements_modern.txt` for library dependencies.

## Installation & Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/DineshDK176/SDAW.git
    cd SDAW
    ```

2.  **Setup & Run**:
    Double-click `setup_and_build.bat` to install dependencies and build the executable automatically.
    
    *Or manually:*
    ```bash
    pip install -r requirements_modern.txt
    python SDAW_Modern.py
    ```

3.  **Building Executable**:
    Run the build script to generate a standalone `.exe`:
    ```bash
    python build_script.py
    ```
    The output file `SDAW_Assistant.exe` will be in the `dist` folder.

## File Structure

- `SDAW_Modern.py`: Main application source code.
- `requirements_modern.txt`: List of dependencies.
- `build_script.py`: PyInstaller script for building the executable.
- `.venv/Assests/`: Directory containing UI assets (icons, GIFs).

## Configuration

- **API Keys**: WolframAlpha API Key is hardcoded in `SDAW_Modern.py`. Replace `UXA89R7337` with your own key if needed.

## Troubleshooting

- **Voice Recognition Errors**: Ensure your microphone is set as the default recording device in Windows.
- **Internet Issues**: The app will automatically disable online features (Search, YouTube) if no connection is detected. Text input works for offline commands (e.g., launching apps).
