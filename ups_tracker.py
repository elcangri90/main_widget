import tkinter as tk
from tkinter import ttk
import base64
import requests
from datetime import datetime

# ============================
# UPS PRODUCTION ENDPOINTS
# ============================
TOKEN_URL = "https://onlinetools.ups.com/security/v1/oauth/token"
TRACK_URL = "https://onlinetools.ups.com/api/track/v1/details/"

# ============================
# YOUR UPS CREDENTIALS
# ============================
CLIENT_ID = "1lasVvgYvQhnF8TdbHfIKJRdfXlKBlj2TIzEu2kDcSQiP7yw"
CLIENT_SECRET = "snqnAPpvGgeYbegkRVBLw5Z3c49BRxYGIjrxM79sVNAY0DIA4nCAWJS5lBF9WEiK"

# ============================
# GET UPS TOKEN
# ============================
def get_token():
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_base64}"
    }

    data = {"grant_type": "client_credentials"}

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code != 200:
        return None

    return response.json()["access_token"]

# ============================
# TRACK PACKAGE
# ============================
def track_package(tracking_number, token):
    url = TRACK_URL + tracking_number
    headers = {
        "Authorization": f"Bearer {token}",
        "transId": "12345",
        "transactionSrc": "testing"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# ============================
# EXTRACT USEFUL INFO
# ============================
def extract_ups_summary(data):
    try:
        shipment = data["trackResponse"]["shipment"][0]
        pkg = shipment["package"][0]
        last_event = pkg["activity"][0]

        return {
            "tracking_number": pkg["trackingNumber"],
            "status": pkg["currentStatus"]["description"],
            "last_update": last_event["status"]["description"],
            "last_city": last_event["location"]["address"].get("city", "Unknown"),

            "date": last_event["date"],
            "time": last_event["time"],

            "date_eu": datetime.strptime(last_event["date"], "%Y%m%d").strftime("%d/%m/%Y"),
            "time_eu": datetime.strptime(last_event["time"], "%H%M%S").strftime("%H:%M"),
        }

    except Exception as e:
        return {"error": str(e)}

# ============================
# DARK BUTTON (same as your Address Search)
# ============================
def dark_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg="gray25",
        fg="white",
        font=("Segoe UI", 8, "bold"),
        relief="flat",
        width=12,
        height=2,
        padx=0,
        pady=0
    )

# ============================
# UPS TRACKER WINDOW (UPDATED)
# ============================
def open_ups_tracker(root, open_windows, close_window):
    key = "ups_tracker"

    # Prevent duplicate windows
    if key in open_windows:
        kind, win = open_windows[key]
        if win.winfo_exists():
            win.lift()
            win.focus_force()
            return
        else:
            del open_windows[key]

    # Create window
    win = tk.Toplevel(root)
    win.title("UPS Tracker")
    win.configure(bg="black")
    win.attributes("-topmost", True)
    win.resizable(False, False)

    open_windows[key] = ("window", win)
    win.protocol("WM_DELETE_WINDOW", lambda: close_window(key))

    # Center window
    win.update_idletasks()
    width = 320
    natural_height = win.winfo_reqheight()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - natural_height) // 2
    win.geometry(f"{width}x{natural_height}+{x}+{y}")

    # -----------------------------
    # LEFT PANEL
    # -----------------------------
    left_frame = tk.Frame(win, bg="black")
    left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    entry = tk.Text(
        left_frame,
        width=32,
        height=3,
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
        relief="flat",
        font=("Segoe UI", 10)
    )
    entry.pack(pady=2, anchor="w")

    # Result box (same style as Address Search)
    result_box = tk.Text(
        left_frame,
        width=32,
        height=10,
        bg="black",
        fg="white",
        insertbackground="white",
        relief="flat",
        font=("Segoe UI", 10)
    )
    result_box.pack(pady=2, anchor="w")
    result_box.config(state="disabled")

    # Color tags
    result_box.tag_config("green", foreground="lime")
    result_box.tag_config("orange", foreground="orange")
    result_box.tag_config("red", foreground="red")
    result_box.tag_config("white", foreground="white")
    result_box.tag_config("center", justify="center")

    # -----------------------------
    # LOGIC
    # -----------------------------
    def show_summary(summary):
        result_box.config(state="normal")
        result_box.delete("1.0", "end")

        if "error" in summary:
            result_box.insert("end", f"Error: {summary['error']}", ("red", "center"))
            result_box.config(state="disabled")
            return

        text = (
            f"Tracking: {summary['tracking_number']}\n"
            f"Status: {summary['status']}\n"
            f"Update: {summary['last_update']}\n"
            f"City: {summary['last_city']}\n"
            f"Date: {summary['date_eu']}\n"
            f"Time: {summary['time_eu']}\n"
        )

        result_box.insert("end", text, ("white",))
        result_box.config(state="disabled")

    def track_now():
        result_box.config(state="normal")
        result_box.delete("1.0", "end")
        result_box.config(state="disabled")

        tracking_number = entry.get("1.0", "end").strip()
        if not tracking_number:
            result_box.config(state="normal")
            result_box.insert("end", "Enter tracking number", ("white", "center"))
            result_box.config(state="disabled")
            return

        token = get_token()
        if not token:
            result_box.config(state="normal")
            result_box.insert("end", "Token error", ("red", "center"))
            result_box.config(state="disabled")
            return

        data = track_package(tracking_number, token)
        summary = extract_ups_summary(data)
        show_summary(summary)

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

    # -----------------------------
    # RIGHT PANEL (vertical buttons)
    # -----------------------------
    button_frame = tk.Frame(win, bg="black")
    button_frame.pack(side="right", fill="y", padx=1, pady=5)

    dark_button(button_frame, text="Track", command=track_now).pack(pady=3)
    dark_button(button_frame, text="Copy", command=copy_result).pack(pady=3)
    dark_button(button_frame, text="Clear", command=clear).pack(pady=3)
