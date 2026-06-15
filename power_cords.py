import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd


def open_cords_lookup(root, open_windows, close_window):
    key = "reg_lookup"

    # If already open → bring to front
    if key in open_windows:
        kind, win = open_windows[key]
        if kind == "window" and win.winfo_exists():
            if win.state() == "iconic":
                win.state("normal")
            win.lift()
            win.focus_force()
            return

    # Load CSV safely
    try:
        reg_df = pd.read_csv("power_cords.csv", dtype=str)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot load power_cords.csv:\n{e}")
        return

    # Build lookup map
    reg_map = {}

    for _, row in reg_df.iterrows():
        cty = row.get("CTY")  # <-- Correct column name
        cord = row.get("power_cord")  # <-- Correct column name

        if not isinstance(cty, str):
            continue

        code = cty.strip().upper()
        cord = cord.strip() if isinstance(cord, str) else ""

        reg_map[code] = cord

    # Create window
    win = tk.Toplevel(root)
    win.title("Power Cord Lookup")
    win.attributes("-topmost", True)
    win.resizable(False, False)
    win.configure(bg="black")

    open_windows[key] = ("window", win)
    win.protocol("WM_DELETE_WINDOW", lambda: close_window(key))

    # Center window
    win.update_idletasks()
    w, h = 350, 180
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw - w) // 2, (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    # Title
    tk.Label(
        win,
        text="Power Cord Lookup",
        bg="black",
        fg="white",
        font=("Segoe UI Semibold", 12)
    ).pack(pady=(10, 5))

    # Input
    entry = tk.Entry(
        win,
        width=10,
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
        relief="flat",
        font=("Segoe UI", 12),
        justify="center"
    )
    entry.pack(pady=5)
    entry.focus()

    # Result label
    result_label = tk.Label(
        win,
        text="",
        bg="black",
        fg="white",
        font=("Segoe UI", 10),
        justify="left"
    )
    result_label.pack(pady=5)

    # Lookup logic
    def lookup():
        code = entry.get().strip().upper()
        if not code:
            result_label.config(text="Enter a country code")
            return

        if code not in reg_map:
            result_label.config(text="❌ Country code not found")
            return

        cord = reg_map[code]
        result_label.config(text=f"🌍 Country: {code}\n🔌 Power Cord: {cord}")

    # Copy result
    def copy_result():
        txt = result_label.cget("text")
        if txt.strip():
            win.clipboard_clear()
            win.clipboard_append(txt)
            popup = tk.Label(win, text="Copied!", bg="deepskyblue")
            popup.place(relx=0.5, rely=0.5, anchor="center")
            win.after(400, popup.destroy)

    # Buttons
    btn_frame = tk.Frame(win, bg="black")
    btn_frame.pack(pady=5)

    style = ttk.Style()
    style.configure(
        "RegBtn.TButton",
        background="#3c3c3c",
        foreground="white",
        padding=6,
        relief="flat"
    )
    style.map(
        "RegBtn.TButton",
        background=[("active", "#4a4a4a")],
        foreground=[("active", "dodgerblue")]
    )

    ttk.Button(btn_frame, text="Lookup", style="RegBtn.TButton", command=lookup).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Copy", style="RegBtn.TButton", command=copy_result).pack(side="left", padx=5)
    ttk.Button(
        btn_frame,
        text="Clear",
        style="RegBtn.TButton",
        command=lambda: (entry.delete(0, tk.END), result_label.config(text=""))
    ).pack(side="left", padx=5)

    win.bind("<Return>", lambda e: lookup())
    win.bind("<Escape>", lambda e: close_window(key))
