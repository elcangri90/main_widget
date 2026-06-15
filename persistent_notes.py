import tkinter as tk
import os
from tkinter import messagebox

def open_persistent_notes(root, open_windows, close_window):
    key = "persistent_notes"  # <-- REQUIRED
    notes_file = "persistent_notes.txt"

    if key in open_windows:
        kind, win = open_windows[key]
        if kind == "window" and win.winfo_exists():
            ...
            return

        # If minimized → restore
        if win.state() == "iconic":
            win.state("normal")

        # Recenter window
        width, height = 350, 250
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

        # Bring to front
        win.lift()
        win.focus_force()
        return

    # --- Create window ---
    win = tk.Toplevel(root)
    win.title("Notes")
    win.attributes("-topmost", True)
    win.resizable(True, True)

    # Temporary size before autosize
    win.geometry("250x250")

    open_windows[key] = ("window", win)

    # --- Text widget ---
    text = tk.Text(
        win,
        wrap="word",
        undo=True,
        bg="gray14",  # background
        fg="white",  # text color
        insertbackground="white",  # cursor color
        relief="flat",  # modern flat look
        highlightthickness=1,
        highlightbackground="white",
        highlightcolor="white"
    )
    text.pack(fill="both", expand=True, padx=5, pady=5)

    # --- Load previous content ---
    if os.path.exists(notes_file):
        try:
            with open(notes_file, "r", encoding="utf-8") as f:
                text.insert("1.0", f.read())
            text.edit_reset()
        except:
            pass

    # --- Center window ONCE ---
    def center_window_once():
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = (screen_w // 2) - (w // 2)
        y = (screen_h // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

    # --- Save function ---
    def save_notes(event=None):
        try:

            #win.autosize_enabled = False

            with open(notes_file, "w", encoding="utf-8") as f:
                f.write(text.get("1.0", "end-1c"))

            # Light popup that disappears
            popup = tk.Label(win, text="Saved", bg="royalblue", fg="black")
            popup.place(relx=0.5, rely=0.5, anchor="center")
            win.after(350, popup.destroy)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

        return "break"

    # --- Undo / Redo ---
    def undo(event=None):
        try:
            text.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def redo(event=None):
        try:
            text.edit_redo()
        except tk.TclError:
            pass
        return "break"

    # --- Add separators so each keypress is undoable ---
    def add_separator(event=None):
        text.edit_separator()
        return None

    # --- Close with ESC ---
    # --- Close with ESC ---
    def close_on_esc(event=None):
        close_window(key)
        return "break"

    win.bind("<Escape>", close_on_esc)

    # --- Proper close button handling ---
    win.protocol("WM_DELETE_WINDOW", lambda: close_window(key))

    # --- Bind shortcuts ---
    text.bind("<Control-s>", save_notes)
    text.bind("<Control-z>", undo)
    text.bind("<Control-y>", redo)
    text.bind("<Key>", add_separator)