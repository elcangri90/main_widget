import os
import webbrowser
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
from tkinterdnd2 import TkinterDnD
from datetime import datetime, timedelta
import sys
from regulatory import open_reg_lookup
from monitor_controls import open_monitor_controls
from restore_minimize import restore_minimized_windows
from power_cords import open_cords_lookup
from pricing_tool import open_pricing_tool
from calculator import open_calculator
from no_adobe import open_pdf_viewer
from address_lookup import open_address_search

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
    root.after(600, popup.destroy)

parameters = """
------------------------------------------------
Dear @

Customer XXXXXX$X | SO PXXXXXX | CL.

Thank you for your help.

Kind regards,
Raffaele
------------------------------------------------
marketing-eu@masimo.com
------------------------------------------------
Country - SO # - Sales Market Not approved - amount $$
------------------------------------------------
Italy → INW → Lisa Cora
Italy → INE → Francesca Pagani
Italy → IC1 → Mila Poli
Italy → IC2 → Giorgia Atturo
Italy → IC3 → Giorgia Atturo
Italy → ISE → Umberto Salvatore
Italy → ISN → Umberto Salvatore
Italy → ISW → Umberto Salvatore
------------------------------------------------
OPERATIONS REQUESTED BOM CHANGE - Original P/N : xx (line x.xx) - New P/N : yyyyyy ; order taker initials, date
OPERATIONS REQUESTED BOM CHANGE - Original P/N : xx (line x.xx) - Cancelled - order taker initials, date
------------------------------------------------
France: MA0550$E
Germany/Poland: MA0420$E
UK: MA0430$E
Austria: MA0480$E
BENELUX: MA0440$E
Switzerland: MA0100$H
Sweden/Denmark: MS0080$I
Portugal/SPAIN: MA0480$E
Italy: IT0010$E
Singapore: MA0600$I
China: BE0040$I
South Africa: KK0020$I
Colombia: JP0020$I
Brazil: MA0031$B
Mexico: TB0010$I
Argentina: MA0100$M
Hong Kong: Bill-to UT0000$I, ship-to MK1000$S
------------------------------------------------
"""
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
root.geometry("1350x220")

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

    # Extraire uniquement les fenêtres Tkinter
    wins = []

    for k, (kind, w) in open_windows.items():
        if kind != "window":
            continue  # ignorer les processus externes

        if k == "pdf_reader":
            continue

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

def show_parameters():
    key = "parameters_infos"

    # If already open → notify + bring to front
    if key in open_windows:
        kind, win = open_windows[key]
        if kind == "window" and win.winfo_exists():
            notify("already open")
            if win.state() == "iconic":
                win.state("normal")
            win.lift()
            win.focus_force()
            return

    # --- Create window ---
    info_window = tk.Toplevel(root)
    info_window.title("Parameters Info")
    info_window.attributes("-topmost", True)
    info_window.resizable(False, False)
    info_window.configure(bg="black")

    # --- Center window ---
    center_window(info_window, 600, 530)

    # --- Text widget (dark mode) ---
    text_widget = tk.Text(
        info_window,
        wrap="word",
        width=60,
        height=25,
        bg="#1b1b1b",
        fg="white",
        insertbackground="white",
        relief="flat",
        font=("Segoe UI", 10),
        highlightthickness=1,
        highlightbackground="#3c3c3c",
        highlightcolor="#4a90e2"
    )
    text_widget.pack(fill="both", expand=True, padx=10, pady=10)

    text_widget.insert("1.0", parameters)
    text_widget.configure(state="normal")

    # --- Close on ESC ---
    def close_on_esc(event=None):
        info_window.destroy()
        return "break"

    info_window.bind("<Escape>", close_on_esc)

    # Track window
    open_windows[key] = ("window", info_window)
    info_window.protocol("WM_DELETE_WINDOW", lambda: close_window(key))


    # --- Track window ---
    open_windows[key] = ("window", info_window)

    info_window.protocol("WM_DELETE_WINDOW", lambda: close_window(key))

def open_persistent_notes():
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
    launcher.update_idletasks()
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

    root.after(700, popup.destroy)

#=== launch BO report ===#

def open_bo_mis_folder():

    path = r"\\CHNEUPFIL01\Groups\CS\Report\00. BO_MIS with ETA.xlsb"
    os.startfile(path)


def dark_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg="gray25",
        fg="white",
        font=("Segoe UI", 18, "bold"),   # bigger emoji/text
        relief="flat",
        width=10,                         # equal width (in text units)
        height=2,                        # equal height (in text units)
        padx=0,
        pady=0
    )

button_grid = tk.Frame(root, bg="black")
button_grid.pack(pady=10, anchor="center")

# Row 0 (REORDERED)

btn_restore_2 = dark_button(button_grid,"📐",align_open_windows_left)
btn_restore_2.configure(bg="darkblue", activebackground="darkblue")  # <-- custom dark color
btn_restore_2.grid(row=0, column=0, padx=8, pady=6)

dark_button(button_grid,"💰", lambda: open_pricing_tool(root, open_windows, close_window)).grid(row=0, column=1, padx=8, pady=6)
dark_button(button_grid, "📍",lambda: open_address_search(root, open_windows, close_window)).grid(row=0, column=2, padx=8, pady=6)

dark_button(button_grid,"📄",lambda: open_pdf_viewer(root, open_windows, close_window)).grid(row=0, column=3, padx=8, pady=6)
dark_button(button_grid, " ", empty_message()).grid(row=0, column=4, padx=8, pady=6)
dark_button(button_grid, "⚡", lambda: open_cords_lookup(root, open_windows, close_window)).grid(row=0, column=5, padx=8, pady=6)
dark_button(button_grid, "📦", open_bo_mis_folder).grid(row=0, column=6, padx=8, pady=6)

btn_restore_1 = dark_button(button_grid,"🔅",lambda: open_monitor_controls(root, open_windows, close_window))
btn_restore_1.configure(bg="yellow", activebackground="yellow", foreground="black")
btn_restore_1.grid(row=0, column=7, padx=8, pady=6)
# Row 1 (unchanged)
dark_button(button_grid, "📝", open_persistent_notes).grid(row=1, column=0, padx=8, pady=6)
dark_button(button_grid, "📸", show_stored_image).grid(row=1, column=1, padx=8, pady=6)
dark_button(button_grid, "📫", open_mailbox_launcher).grid(row=1, column=2, padx=8, pady=6)
dark_button(button_grid,"π",lambda: open_calculator(root, open_windows, close_window)).grid(row=1, column=3, padx=8, pady=6)

dark_button(button_grid, "🛈", show_parameters).grid(row=1, column=4, padx=8, pady=6)
dark_button(button_grid, "⚖️", lambda: open_reg_lookup(root, open_windows, close_window)).grid(row=1, column=5, padx=8, pady=6)
dark_button(button_grid, "🔁", launch_file_exchanger).grid(row=1, column=6, padx=8, pady=6)

btn_restore = dark_button(button_grid,"💨",lambda: restore_minimized_windows(root, open_windows))
btn_restore.configure(bg="darkblue", activebackground="darkblue")  # <-- custom dark color
btn_restore.grid(row=1, column=7, padx=8, pady=6)

root.mainloop()