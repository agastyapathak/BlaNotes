"""
BlaNotes
 Agastya Pathak.
Distribution Code: v3 - 27.09.2026
 commands:
   /history   - show all saved notes
    /delete    - delete a note (by number) or all notes
    /download  - export all notes to 'BlaNotes History.txt' and open it
    /help      - show the command list again
    /exit      - quit the app
    /font      - font style
"""
import json
import os
import shutil
import sys
import webbrowser
from datetime import datetime

if sys.platform == "win32":
    import msvcrt
else:
    import termios
    import tty

NOTES_FILE = "blanotes_history.json"
EXPORT_FILE = "BlaNotes History.txt"


#Ollama AI feature soon...
AI_TOOLS = (
    ("Ollama", "with Ollama", ("ollama",), ("~/.ollama",), ()),
    ("Claude Code", "with Claude Code", ("claude",),
     ("~/.claude", "~/.claude.json", "~/.config/claude"),
     ("anthropic.claude-code",)),
    ("Kilo Code", "with Kilo Code", ("kilo",),
     ("~/.kilo", ".kilo", "~/.config/kilo"),
     ("kilocode.kilo-code",)),
    ("Gemini CLI", "with Gemini", ("gemini",),
     ("~/.gemini", "~/.config/gemini"),
     ("google.gemini-cli",)),
)

EDITOR_EXTENSION_DIRS = (
    "~/.vscode/extensions",
    "~/.vscode-insiders/extensions",
    "~/.cursor/extensions",
    "~/.windsurf/extensions",
    "~/.vscode-oss/extensions",
)


def list_dir(path):
    """Return entry names in a directory, or an empty set if it is unreadable."""
    try:
        return set(os.listdir(os.path.expanduser(path)))
    except OSError:
        return set()


def detect_ai_tools():
 
   
    found = []
    try:
        extensions = set()
        for extension_dir in EDITOR_EXTENSION_DIRS:
            extensions |= list_dir(extension_dir)

        for name, tagline, binaries, paths, extension_ids in AI_TOOLS:
            source = None
            for binary in binaries:
                if shutil.which(binary):
                    source = f"{binary} on PATH"
                    break
            if not source:
                for path in paths:
                    if os.path.exists(os.path.expanduser(path)):
                        source = path
                        break
            if not source:
                for extension_id in extension_ids:
                    match = next(
                        (e for e in extensions if e.lower().startswith(extension_id)),
                        None,
                    )
                    if match:
                        source = f"editor extension {match}"
                        break
            if source:
                found.append((name, tagline, source))
    except Exception:
        return found
    return found


def show_ai_notifications():

    for name, tagline, source in detect_ai_tools():
        print(f"🤖 {name} detected ({source}) - BlaAI coming soon with Ollama {tagline}!")


# ANSI ESCAPE CODES
FONT_RESET = "\033[0m"
FONT_BOLD = "\033[1m"
FONT_ITALIC = "\033[3m"
FONT_UNDERLINE = "\033[4m"

FONT_STYLES = {
    'b': FONT_BOLD,
    'i': FONT_ITALIC,
    'u': FONT_UNDERLINE,
    'n': FONT_RESET,
}


def get_key():
    """Read a single keypress from stdin (cross-platform)."""
    if sys.platform == "win32":
        ch = msvcrt.getwch()
        # Handle special keys (arrow keys, function keys, etc.)
        if ch == '\x00' or ch == '\xe0':
            ch += msvcrt.getwch()
        return ch
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            # Handle escape sequences (arrow keys, etc.)
            if ch == '\x1b':
                ch += sys.stdin.read(2)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def font_mode_input(prompt="Font mode > "):
    """
    Interactive font styling input mode.
    Supports: /font i (italic), /font b (bold), /font u (underline), /font n (normal)
    Press Escape to exit font mode.
    Returns the styled text.
    """
    print(f"\n📝 Font Mode: Type text with styling. Commands: /font i|b|u|n | Esc to exit")
    print(f"{prompt}", end="", flush=True)
    
    styled_text = ""
    current_style = ""
    buffer = ""
    in_font_command = False
    font_cmd_buffer = ""
    
    while True:
        key = get_key()
        
        # Handle Escape key (exit font mode)
        if key == '\x1b' or key == '\x1b\x1b':
            print(f"\n{FONT_RESET}✅ Font mode exited.")
            return styled_text
        
        # Handle Enter key
        if key in ('\n', '\r'):
            print()
            continue
        
        # Handle Backspace/Delete
        if key in ('\x7f', '\x08'):  # Backspace
            if buffer:
                buffer = buffer[:-1]
                # Recalculate styled_text from buffer
                styled_text = ""
                current_style = ""
                i = 0
                while i < len(buffer):
                    if buffer[i:i+6] == "/font ":
                        if i + 7 <= len(buffer):
                            cmd = buffer[i+6]
                            if cmd in FONT_STYLES:
                                current_style = FONT_STYLES[cmd]
                                i += 7
                                continue
                    styled_text += current_style + buffer[i] if buffer[i] != '\n' else buffer[i]
                    i += 1
                # Redraw line
                print(f"\r{prompt}{' ' * 80}\r{prompt}{styled_text}{FONT_RESET}", end="", flush=True)
            continue
        
        # Handle regular characters
        if key.isprintable() or key in (' ', '\t'):
            buffer += key
            
            # Check for /font command
            if buffer.endswith("/font "):
                in_font_command = True
                font_cmd_buffer = ""
                continue
            
            if in_font_command:
                font_cmd_buffer += key
                if font_cmd_buffer in ('i', 'b', 'u', 'n'):
                    # Apply the style
                    current_style = FONT_STYLES[font_cmd_buffer]
                    in_font_command = False
                    font_cmd_buffer = ""
                    # Don't add the command to styled output
                    continue
                elif len(font_cmd_buffer) > 1:
                    # Invalid command, treat as regular text
                    in_font_command = False
                    font_cmd_buffer = ""
            
            # Add character with current style
            if not in_font_command:
                styled_text += current_style + key
                print(f"{current_style}{key}{FONT_RESET}", end="", flush=True)


def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def add_note(notes, text):
    notes.append({
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_notes(notes)
    print("✅ Note saved.")


def show_history(notes):
    if not notes:
        print("📭 No notes yet.")
        return
    print("\n📜 Note history:")
    for i, note in enumerate(notes, start=1):
        print(f"  {i}. [{note['timestamp']}] {note['text']}")
    print()


def delete_notes(notes):
    if not notes:
        print("Process interupted. No notes to delete…")
        return notes

    show_history(notes)
    choice = input("Enter note number to delete, 'all' to delete everything, "
                    "or press Enter to cancel: ").strip()

# delete_notes 
    if choice == "":
        print("Cancelled.")
    elif choice.lower() == "all":
        confirm = input("Are you sure you want to delete ALL notes? (yes/no): ").strip().lower()
        if confirm == "yes":
            notes = []
            save_notes(notes)
            print("🗑️  All notes deleted.")
        else:
            print("Cancelled.")
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(notes):
                removed = notes.pop(index)
                save_notes(notes)
                print(f" Deleted note: {removed['text']}")
            else:
                print("⚠️Invalid function.")
        except ValueError:
            print("⚠️  Invalid input.")

    return notes


def download_notes(notes):
    if not notes:
        print("📭 No notes to download.")
        return

    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        for i, note in enumerate(notes, start=1):
            f.write(f"{i}. [{note['timestamp']}] {note['text']}\n")

    print(f"💾 Notes exported to '{EXPORT_FILE}'")


def print_help():
    print("""
Commands:
    /history   - show all saved notes
    /delete    - delete a note (by number) or all notes
    /download  - export all notes to 'BlaNotes History.txt' and open it
    /github    - open GitHub profile
    /help      - show this help message
    /exit      - quit the app
    /font      - font style
""")


def open_github():
    webbrowser.open("https://github.com/agastyapathak")
    print("🌐 Opening GitHub profile...")


def main():
    notes = load_notes()
    print("📝 Welcome to BlaNotes!")
    show_ai_notifications()
    print_help()

    while True:
        user_input = input("BlaNotes > ").strip()

        if user_input == "":
            continue
        elif user_input.lower() == "/exit":
            print("Programm interupted. Exiting BlaNotes...")
            break
        elif user_input.lower() == "/history":
            show_history(notes)
        elif user_input.lower() == "/delete":
            notes = delete_notes(notes)
        elif user_input.lower() == "/download":
            download_notes(notes)
        elif user_input.lower() == "/github":
            open_github()
        elif user_input.lower() == "/help":
            print_help()
        elif user_input.lower() == "/font":
            styled_text = font_mode_input()
            if styled_text:
                add_note(notes, styled_text)
        else:
            add_note(notes, user_input)


if __name__ == "__main__":
    main()
