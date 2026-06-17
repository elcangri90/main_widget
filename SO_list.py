import os
import webbrowser
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
from tkinterdnd2 import TkinterDnD
from datetime import datetime, timedelta
from regulatory import open_reg_lookup
from monitor_controls import open_monitor_controls
from restore_minimize import restore_minimized_windows
from power_cords import open_cords_lookup
from pricing_tool import open_pricing_tool
from calculator import open_calculator
from address_lookup import open_address_search
import sys
from persistent_notes import open_persistent_notes
from UPS_tracker import open_ups_tracker

open_windows = {}

highlight_locked = True

def close_window(name):
    if name in open_windows:
        kind, win = open_windows[name]
        if kind == "window":
            try:
                win.destroy()
            except:
                pass
        del open_windows[name]


def notify(msg):
    popup = tk.Label(root, text=msg, bg="yellow")
    popup.place(relx=0.5, rely=0.5, anchor="center")
    root.after(500, popup.destroy)

def center_main_window(win, width=None, height=None):
    win.update_idletasks()

    # If width/height not provided, use current size
    w = width if width else win.winfo_width()
    h = height if height else win.winfo_height()

    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()

    x = (screen_w // 2) - (w // 2)
    y = (screen_h // 2) - (h // 2)

    win.geometry(f"{w}x{h}+{x}+{y}")

# === GUI Setup ===
root = TkinterDnD.Tk()
root.title("Main widget")
root.attributes("-topmost", True)
root.resizable(False, False)
root.configure(bg="black")
open_windows["csv_editor"] = ("window", root)

# === Minimize / Restore all windows when main CSV editor is minimized ===

def minimize_all(event=None):
    if root.state() == "iconic":
        for name, (kind, win) in open_windows.items():
            if kind != "window":
                continue
            if win is not root and win.winfo_exists():

                try:
                    win.state("iconic")
                except:
                    pass


def restore_all(event=None):
    if root.state() == "normal":
        for name, (kind, win) in open_windows.items():
            if kind != "window":
                continue

            if win is not root and win.winfo_exists():
                try:
                    win.state("normal")
                except:
                    pass


root.bind("<Unmap>", minimize_all)
root.bind("<Map>", restore_all)

# Set an initial size so Tkinter doesn't think it's 1x1
root.geometry("920x180")

root.update_idletasks()
center_main_window(root)

style = ttk.Style()
style.theme_use("clam")

# --- Prevent main window from shrinking ---
root.update_idletasks()
root.minsize(root.winfo_width(), root.winfo_height())

# Make all ttk frames black
style.configure("TFrame", background="black")

# Make Treeview dark
style.configure(
    "Treeview",
    background="black",
    fieldbackground="black",
    foreground="white",
    bordercolor="black",
    borderwidth=0
)

style.configure(
    "Treeview.Heading",
    background="black",
    foreground="white",
    font=("Comic Sans MS", 10, "italic")
)

# Remove Treeview highlight border
style.map("Treeview", background=[("selected", "#333333")])
# === Table Frame ===
table_frame = ttk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=0, pady=0)


# --- Prevent Treeview from forcing window shrink ---
table_frame.pack_propagate(False)

# === Top Bar (Search + Buttons) ===
top_bar = tk.Frame(table_frame, bg="black")
top_bar.pack(fill="x", pady=0)

def align_open_windows_left():
    if not open_windows:
        return

    wins = []

    for k, (kind, w) in open_windows.items():

        # Skip processes
        if kind != "window":
            continue

        # Skip excluded windows
        if k in ("PDFViewer","cus_infos"):
            continue

        # Only add existing windows
        if w.winfo_exists():
            wins.append(w)

    if not wins:
        return

    # Trier par largeur
    for w in wins:
        w.update_idletasks()

    wins.sort(key=lambda w: w.winfo_width())

    screen_h = wins[0].winfo_screenheight()
    px_per_cm = 37.8
    bottom_pad = int(4 * px_per_cm)
    spacing = int(1 * px_per_cm)

    total_h = sum(w.winfo_height() for w in wins) + spacing * (len(wins) - 1) + bottom_pad
    y = screen_h - total_h
    x = 35

    for i, w in enumerate(wins):
        h = w.winfo_height()
        w.geometry(f"+{x}+{y}")
        y += h
        if i < len(wins) - 1:
            y += spacing

# Buttons (RIGHT)
buttons_frame = tk.Frame(top_bar, bg="black")
buttons_frame.pack(side="right", padx=5)

# === Treeview ===
tree = ttk.Treeview(
    table_frame,
    show="tree",   # no columns, only a tree structure
    selectmode="browse"
)

# Disable default selection highlight
style.map("Treeview",
          background=[("selected", "#1E90FF")],  # DodgerBlue
          foreground=[("selected", "white")])


def unlock_highlight(event=None):
    global highlight_locked
    highlight_locked = False

tree.bind("<Button-1>", unlock_highlight)

def center_window(win, width, height):
    win.update_idletasks()  # ensures correct geometry

    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()

    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)

    win.geometry(f"{width}x{height}+{x}+{y}")

def show_stored_image():
    if not os.path.exists("stored_image.png"):
        messagebox.showinfo("Image", "No stored image found.")
        return

    img_win = tk.Toplevel(root)
    img_win.title("Stored Image")
    img_win.attributes("-topmost", True)
    img_win.resizable(False, False)

    # --- Load image and keep reference ---
    img_win.stored_img = tk.PhotoImage(file="stored_image.png")
    tk.Label(img_win, image=img_win.stored_img).pack()

    # --- Center the window ---
    img_win.update_idletasks()
    w = img_win.winfo_width()
    h = img_win.winfo_height()
    sw = img_win.winfo_screenwidth()
    sh = img_win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    img_win.geometry(f"{w}x{h}+{x}+{y}")

    # --- Close on ESC ---
    def close_on_esc(event=None):
        img_win.destroy()
        return "break"

    img_win.bind("<Escape>", close_on_esc)


def open_mailbox_launcher():
    launcher = tk.Toplevel(root)
    launcher.title("mailboxes")
    launcher.attributes("-topmost", True)
    launcher.resizable(False, False)
    launcher.configure(bg="black")

    # Center the window
    w, h = 250, 250
    sw = launcher.winfo_screenwidth()
    sh = launcher.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    launcher.geometry(f"{w}x{h}+{x}+{y}")

    # Your 4 mailboxes
    mailboxes = {
        "Raffaele (Main)": "https://outlook.office.com/mail/raffaele.beffa@masimo.com/",
        "EMEA Sales": "https://outlook.office.com/mail/emeasales@masimo.com/",
        "Distributor International": "https://outlook.office.com/mail/distributorinternati@masimo.com/",
        "Indian Sales": "https://outlook.office.com/mail/indiansales@masimo.com/",
        "Latam": "https://outlook.cloud.microsoft/mail/LATAMSales@masimo.com/"
    }

    # Store checkbox variables
    vars_dict = {}

    # Checkbox frame
    frame = ttk.Frame(launcher)
    frame.pack(pady=5)

    # --- Checkbox style ---
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "BlackCheck.TCheckbutton",
        background="black",
        foreground="white",
    )

    style.map(
        "BlackCheck.TCheckbutton",
        foreground=[("selected", "white")],
        background=[("selected", "black")],
        indicatorcolor=[("selected", "black"), ("!selected", "gray30")],
    )

    # Create checkboxes
    for i, (name, url) in enumerate(mailboxes.items()):
        var = tk.BooleanVar()
        chk = ttk.Checkbutton(frame, text=name, variable=var, style="BlackCheck.TCheckbutton")
        chk.grid(row=i, column=0, sticky="w", padx=10, pady=(3, 3))
        vars_dict[name] = var

    # Toggle Select All button
    def toggle_select_all():
        # Check if all are already selected
        all_selected = all(var.get() for var in vars_dict.values())

        # If all selected → deselect all
        # If not all selected → select all
        for var in vars_dict.values():
            var.set(not all_selected)

    tk.Button(
        launcher,
        text="Select All",
        bg="gray14",
        fg="white",
        command=toggle_select_all).pack(pady=(10, 3))

    # Launch button
    def launch_selected():
        selected_urls = [
            mailboxes[name]
            for name, var in vars_dict.items()
            if var.get()
        ]

        if not selected_urls:
            messagebox.showwarning("No selection", "Please select at least one mailbox.")
            return

        for url in selected_urls:
            webbrowser.open_new(url)

        launcher.destroy()

    tk.Button(
        launcher,
        text="Launch Selected",
        bg="gray14",
        fg="white",
        command=launch_selected
    ).pack(pady=5)

    def close_on_esc(event=None):
        launcher.destroy()
        return "break"

    launcher.bind("<Escape>", close_on_esc)

def normalize(value):
    if value is None:
        return ""
    s = str(value)
    s = s.replace(".0", "")
    s = re.sub(r"[\s\u00A0\u2000-\u200B\u202F\u205F\u3000]+", "", s)
    s = s.replace("\x00", "")
    return s.upper()

# ============================================================
# 2. Normalize SO IDs
# ============================================================
def get_cts_info(df, so_id):
    search = normalize(so_id)
    df["SO ID NORMALIZED"] = df["SO ID"].apply(normalize)
    df["ORACLE_SO_ID NORMALIZED"] = df["ORACLE_SO_ID"].apply(normalize)

    result = df[
        (df["SO ID NORMALIZED"] == search) |
        (df["ORACLE_SO_ID NORMALIZED"] == search)
        ]
    return result


def excel_serial_to_date(value):
    try:
        value = float(value)
        base = datetime(1899, 12, 30)
        date = base + timedelta(days=value)
        return date.strftime("%d.%m.%y")
    except:
        return value

 # === launch file exchanger ===#

def launch_file_exchanger():
    key = "file_exchanger"

    # --- If already running ---
    if key in open_windows:
        kind, proc = open_windows[key]

        # Only handle if it's a process
        if kind == "process":
            # If process still alive → do not relaunch
            if proc.poll() is None:
                notify("Already open")
                return
            else:
                # Process ended → remove key
                del open_windows[key]

    # --- Launch external script ---
    script_dir = r"C:\Users\raffaele.beffa\Documents\python\3_docs_exchange"
    script_path = os.path.join(script_dir, "tk_launch.py")

    try:
        proc = subprocess.Popen([sys.executable, script_path], cwd=script_dir)
        open_windows[key] = ("process", proc)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch File Exchanger:\n{e}")

def empty_message():
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)  # pas de bordure
    popup.config(bg="orange")

    label = tk.Label(popup, text="Already open 🌬️", bg="orange", fg="black")
    label.pack(padx=10, pady=5)

    # centrer sur root
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()

    popup.update_idletasks()
    w = popup.winfo_width()
    h = popup.winfo_height()

    popup.geometry(f"{w}x{h}+{root_x + root_w//2 - w//2}+{root_y + root_h//2 - h//2}")

    root.after(500, popup.destroy)

#=== launch BO report ===#

def open_bo_mis_folder():

    path = r"\\CHNEUPFIL01\Groups\CS\Report\00. BO_MIS with ETA.xlsb"
    os.startfile(path)

def open_cus_with_refresh():
    from cus_infos import save_document, open_cus_viewer
    save_document("docs.db", "data.json")
    open_cus_viewer(root, open_windows, close_window)



def dark_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg="gray25",
        fg="white",
        font=("Segoe UI", 15, "bold"),   # bigger emoji/text
        relief="flat",
        width=8,                         # equal width (in text units)
        height=2,                        # equal height (in text units)
        padx=0,
        pady=0
    )

button_grid = tk.Frame(root, bg="black")
button_grid.pack(pady=10, anchor="center")

# Row 0 (REORDERED)

btn_restore_2 = dark_button(button_grid,"📐",align_open_windows_left)
btn_restore_2.configure(bg="darkblue", activebackground="darkblue")
btn_restore_2.grid(row=0, column=0, padx=4, pady=4)

dark_button(button_grid,"💰", lambda: open_pricing_tool(root, open_windows, close_window)).grid(row=0, column=1, padx=4, pady=4)
dark_button(button_grid, "📍",lambda: open_address_search(root, open_windows, close_window)).grid(row=0, column=2, padx=4, pady=4)

dark_button(button_grid, "🚚", lambda: open_ups_tracker(root, open_windows, close_window)).grid(row=0, column=3, padx=4, pady=4)
dark_button(button_grid, "🗄", open_cus_with_refresh).grid(row=0, column=4, padx=4, pady=4)
dark_button(button_grid, "⚡", lambda: open_cords_lookup(root, open_windows, close_window)).grid(row=0, column=5, padx=4, pady=4)
dark_button(button_grid, "📦", open_bo_mis_folder).grid(row=0, column=6, padx=4, pady=4)

dark_button(button_grid,"🔅",lambda: open_monitor_controls(root, open_windows, close_window)).grid(row=0, column=7, padx=4, pady=4)

dark_button(button_grid, "📝",lambda: open_persistent_notes(root,open_windows, close_window)).grid(row=1, column=0, padx=4, pady=4)
dark_button(button_grid, "📸", show_stored_image).grid(row=1, column=1, padx=4, pady=4)
dark_button(button_grid, "📫", open_mailbox_launcher).grid(row=1, column=2, padx=4, pady=4)
dark_button(button_grid,"➗",lambda: open_calculator(root, open_windows, close_window)).grid(row=1, column=3, padx=4, pady=4)
dark_button(button_grid, "", empty_message()).grid(row=1, column=4, padx=4, pady=4)
dark_button(button_grid, "⚖️", lambda: open_reg_lookup(root, open_windows, close_window)).grid(row=1, column=5, padx=4, pady=4)
dark_button(button_grid, "🔁", launch_file_exchanger).grid(row=1, column=6, padx=4, pady=4)

btn_restore = dark_button(button_grid,"💨",lambda: restore_minimized_windows(root, open_windows))
btn_restore.configure(bg="darkblue", activebackground="darkblue")
btn_restore.grid(row=1, column=7, padx=4, pady=4)



root.mainloop()