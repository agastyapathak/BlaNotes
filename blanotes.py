"""
BlaNotes
 Agastya Pathak.

commands:
   /history   - show all saved notes
    /delete    - delete a note (by number) or all notes
    /download  - export all notes to a .txt file
    /help      - show the command list again
    /exit      - quit the app
"""


import json
import os
import webbrowser
from datetime import datetime

NOTES_FILE = "blanotes_history.json"


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

    filename = f"blanotes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for i, note in enumerate(notes, start=1):
            f.write(f"{i}. [{note['timestamp']}] {note['text']}\n")

    print(f"💾 Notes exported to '{filename}'")


def print_help():
    print("""
Commands:
    /history   - show all saved notes
    /delete    - delete a note (by number) or all notes
    /download  - export all notes to a .txt file
    /github    - open GitHub profile
    /help      - show this help message
    /exit      - quit the app
""")


def open_github():
    webbrowser.open("https://github.com/agastyapathak")
    print("🌐 Opening GitHub profile...")


def main():
    notes = load_notes()
    print("📝 Welcome to BlaNotes!")
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
        else:
            add_note(notes, user_input)


if __name__ == "__main__":
    main()
