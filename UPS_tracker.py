import tkinter as tk
from tkinter import ttk
import base64
import requests

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
        }
    except Exception as e:
        return {"error": str(e)}


# ============================
# TKINTER SUMMARY WIDGET
# ============================
class UPSTrackingWidget(ttk.Frame):
    def __init__(self, parent, summary):
        super().__init__(parent)
        self.configure(padding=10)

        ttk.Label(self, text="UPS Tracking Summary", font=("Segoe UI", 14, "bold")).pack(pady=5)

        if "error" in summary:
            ttk.Label(self, text="Error: " + summary["error"], foreground="red").pack()
            return

        ttk.Label(self, text=f"Tracking Number: {summary['tracking_number']}").pack(anchor="w")
        ttk.Label(self, text=f"Status: {summary['status']}").pack(anchor="w")
        ttk.Label(self, text=f"Last Update: {summary['last_update']}").pack(anchor="w")
        ttk.Label(self, text=f"Location: {summary['last_city']}").pack(anchor="w")
        ttk.Label(self, text=f"Date: {summary['date']}").pack(anchor="w")
        ttk.Label(self, text=f"Time: {summary['time']}").pack(anchor="w")


# ============================
# UPS TRACKER WINDOW
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
    win.attributes("-topmost", True)
    win.resizable(False, False)
    win.configure(bg="black")

    open_windows[key] = ("window", win)

    # Center window
    win.update_idletasks()
    w, h = 380, 320
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    # Close on ESC
    win.bind("<Escape>", lambda e: close_window(key))

    # UI
    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter UPS Tracking Number:", font=("Segoe UI", 12)).pack()

    entry = ttk.Entry(frame, width=35)
    entry.pack(pady=10)

    result_frame = ttk.Frame(frame)
    result_frame.pack(fill="both", expand=True, pady=10)

    def on_track():
        for widget in result_frame.winfo_children():
            widget.destroy()

        tracking_number = entry.get().strip()
        token = get_token()

        if not token:
            ttk.Label(result_frame, text="Error retrieving token", foreground="red").pack()
            return

        data = track_package(tracking_number, token)
        summary = extract_ups_summary(data)

        widget = UPSTrackingWidget(result_frame, summary)
        widget.pack(fill="x")

    ttk.Button(frame, text="Track Package", command=on_track).pack(pady=10)
