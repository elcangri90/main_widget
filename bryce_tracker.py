# ============================
# MIS DATA EXTRACTOR
# ============================
import requests
import tkinter as tk
from bs4 import BeautifulSoup

def fetch_mis_data(so_id):
    url = "http://bryce/intranet/exapps/get_soid_from_MIS.cfm"
    payload = {"so_id": so_id, "po_id": ""}

    response = requests.post(url, data=payload)
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr")

    ship_dates = []
    tracking_numbers = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 14:
            ship_date = cols[10].text.strip()
            tracking = cols[12].text.strip()

            if ship_date:
                ship_dates.append(ship_date)

            if tracking.lower().startswith("1z"):
                tracking_numbers.append(tracking)

    return {
        "ship_dates": list(set(ship_dates)),
        "tracking_numbers": list(set(tracking_numbers))
    }


# ============================
# MIS TRACKER WINDOW
# ============================
def open_mis_tracker(root, open_windows, close_window):
    key = "mis_tracker"

    if key in open_windows:
        kind, win = open_windows[key]
        if win.winfo_exists():
            win.lift()
            win.focus_force()
            return
        else:
            del open_windows[key]

    win = tk.Toplevel(root)
    win.title("Bryce Tracker")
    win.configure(bg="black")
    win.attributes("-topmost", True)
    win.resizable(False, False)

    open_windows[key] = ("window", win)
    win.protocol("WM_DELETE_WINDOW", lambda: close_window(key))
    win.bind("<Escape>", lambda e: close_window(key))

    # Center window
    win.update_idletasks()
    width = 320
    natural_height = win.winfo_reqheight()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - natural_height) // 2
    win.geometry(f"{width}x{natural_height}+{x}+{y}")

    # LEFT PANEL
    left_frame = tk.Frame(win, bg="black")
    left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    entry = tk.Text(left_frame, width=32, height=3, bg="#2b2b2b", fg="white",
                    insertbackground="white", relief="flat", font=("Segoe UI", 10))
    entry.pack(pady=2, anchor="w")

    result_box = tk.Text(left_frame, width=32, height=10, bg="black", fg="white",
                         insertbackground="white", relief="flat", font=("Segoe UI", 10))
    result_box.pack(pady=2, anchor="w")
    result_box.config(state="disabled")

    # RIGHT PANEL
    button_frame = tk.Frame(win, bg="black")
    button_frame.pack(side="right", fill="y", padx=1, pady=5)

    # -----------------------------
    # LOGIC
    # -----------------------------
    def fetch_mis():
        so_id = entry.get("1.0", "end").strip()

        result_box.config(state="normal")
        result_box.delete("1.0", "end")

        if not so_id:
            result_box.insert("end", "Enter SO_ID", "center")
            result_box.config(state="disabled")
            return

        data = fetch_mis_data(so_id)

        ship_dates = data["ship_dates"]
        tracking_numbers = data["tracking_numbers"]

        result_box.insert("end", f"SO_ID: {so_id}\n\n")

        result_box.insert("end", "Ship Dates:\n")
        for d in ship_dates:
            result_box.insert("end", f" - {d}\n")

        result_box.insert("end", "\nTracking Numbers:\n")
        for t in tracking_numbers:
            result_box.insert("end", f" - {t}\n")

        result_box.config(state="disabled")

    def clear():
        entry.delete("1.0", "end")
        result_box.config(state="normal")
        result_box.delete("1.0", "end")
        result_box.config(state="disabled")

    def copy_result():
        text = result_box.get("1.0", "end").strip()
        if text:
            win.clipboard_clear()
            win.clipboard_append(text)

    def dark_button(parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="gray25",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            width=12,  # equal width (in text units)
            height=2,  # equal height (in text units)
            padx=0,
            pady=0
        )

    button_grid = tk.Frame(root, bg="black")
    button_grid.pack(side="right", fill="y", padx=1, pady=5)

    # Buttons
    dark_button(button_frame, "Track", fetch_mis).pack(pady=3)
    dark_button(button_frame, "Copy", copy_result).pack(pady=3)
    dark_button(button_frame, "Clear", clear).pack(pady=3)
