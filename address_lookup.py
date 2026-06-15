import tkinter as tk
from tkinter import ttk
import pandas as pd
import re
from rapidfuzz import fuzz
import os

# -----------------------------
# Load Excel once
# -----------------------------
excel_df = pd.read_excel("AccountDB_2.xlsx")

swedish_plain_map = {
    "Å": "A", "å": "a",
    "Ä": "A", "ä": "a",
    "Ö": "O", "ö": "o"
}

def normalize_query(raw_query: str) -> str:
    text = raw_query.lower()
    text = re.sub(r"[;,\-/|.,]", " ", text)
    text = re.sub(r"\s+", " ", text)

    for sym, plain in swedish_plain_map.items():
        text = text.replace(sym.lower(), plain.lower())

    return text.strip()

addressDB = [normalize_query(addr) for addr in excel_df["MERGED_ADDRESS"].astype(str).tolist()]

# -----------------------------
# Matching helpers
# -----------------------------
def best_fuzzy_match(query, choices):
    scores = []
    for idx, addr in enumerate(choices):
        s1 = fuzz.token_set_ratio(query, addr)
        s2 = fuzz.partial_ratio(query, addr)
        s3 = fuzz.token_sort_ratio(query, addr)
        score = max(s1, s2, s3)
        scores.append((addr, score, idx))
    return max(scores, key=lambda x: x[1]) if scores else None

def token_overlap(query, choices):
    tokens = query.split()
    candidates = []
    for idx, addr in enumerate(choices):
        overlap = sum(1 for t in tokens if t in addr)
        if overlap > 0:
            percent = int((overlap / len(tokens)) * 100)
            candidates.append((addr, percent, idx))
    return max(candidates, key=lambda x: x[1]) if candidates else None

def top_matches(query, choices, limit=8):
    results = []
    for idx, addr in enumerate(choices):
        s1 = fuzz.token_set_ratio(query, addr)
        s2 = fuzz.partial_ratio(query, addr)
        s3 = fuzz.token_sort_ratio(query, addr)
        score = max(s1, s2, s3)
        results.append((addr, score, idx))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]

# -----------------------------
# Color function
# -----------------------------
def color_for_score(score):
    if score >= 90:
        return "green"
    elif score >= 70:
        return "orange"
    else:
        return "red"

# -----------------------------
# GUI Window
# -----------------------------
def open_address_search(root, open_windows, close_window):
    key = "add_search"

    if key in open_windows:
        kind, win = open_windows[key]
        if kind == "window" and win.winfo_exists():
            win.lift()
            win.focus_force()
            return

    search_win = tk.Toplevel(root)
    search_win.title("Address Search")
    search_win.configure(bg="black")
    search_win.attributes("-topmost", True)
    search_win.resizable(False, False)

    width = 320
    search_win.update_idletasks()
    natural_height = search_win.winfo_reqheight()

    sw = search_win.winfo_screenwidth()
    sh = search_win.winfo_screenheight()

    x = (sw - width) // 2
    y = (sh - natural_height) // 2

    search_win.geometry(f"{width}x{natural_height}+{x}+{y}")

    open_windows[key] = ("window", search_win)
    search_win.protocol("WM_DELETE_WINDOW", lambda: close_window(key))

    # -----------------------------
    # LEFT PANEL
    # -----------------------------
    left_frame = tk.Frame(search_win, bg="black")
    left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    entry = tk.Text(left_frame, width=32, height=3, bg="#2b2b2b", fg="white",
                    insertbackground="white", relief="flat",
                    font=("Segoe UI", 10))
    entry.pack(pady=2, anchor="w")

    entry.bind("<Return>", lambda event: find_best())

    result_box = tk.Text(
        left_frame,
        width=32,
        height=8,
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

    # CENTER TAG
    result_box.tag_config("center", justify="center")

    # -----------------------------
    # LOGIC
    # -----------------------------
    def find_best():
        query = entry.get("1.0", "end").strip()
        result_box.config(state="normal")
        result_box.delete("1.0", "end")

        if not query:
            result_box.insert("end", "Enter an address", ("white", "center"))
            result_box.config(state="disabled")
            return

        norm = normalize_query(query)
        result = best_fuzzy_match(norm, addressDB)

        if not result or result[1] < 70:
            result = token_overlap(norm, addressDB)

        if not result:
            result_box.insert("end", "No match found", ("red", "center"))
            result_box.config(state="disabled")
            return

        addr, score, idx = result
        cid = excel_df.iloc[idx]["CUSTOMER_ID"]
        color = color_for_score(int(score))

        result_box.insert("end", f"{cid}\n{int(score)}%", (color, "center"))
        result_box.config(state="disabled")


    def show_top():
        query = entry.get("1.0", "end").strip()
        result_box.config(state="normal")
        result_box.delete("1.0", "end")

        if not query:
            result_box.insert("end", "Enter an address", ("white", "center"))
            result_box.config(state="disabled")
            return

        norm = normalize_query(query)
        results = top_matches(norm, addressDB)

        for addr, score, idx in results:
            cid = excel_df.iloc[idx]["CUSTOMER_ID"]
            color = color_for_score(int(score))
            result_box.insert("end", f"{cid} {int(score)}%\n", (color, "center"))

        result_box.config(state="disabled")

    def clear():
        entry.delete("1.0", tk.END)
        result_box.config(state="normal")
        result_box.delete("1.0", "end")
        result_box.config(state="disabled")

    def copy_id():
        text = result_box.get("1.0", "end").strip().split("\n")[0]
        if text:
            search_win.clipboard_clear()
            search_win.clipboard_append(text)

    def open_excel():
        file_path = "AccountDB_2.xlsx"
        result_box.config(state="normal")
        result_box.delete("1.0", "end")

        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            result_box.insert("end", "File not found", ("red", "center"))

        result_box.config(state="disabled")

    # button_style.py

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

    button_grid = tk.Frame(search_win, bg="black")
    button_grid.pack(side="right", fill="y", padx=1, pady=5)
    # -----------------------------
    # RIGHT PANEL (vertical buttons)
    # -----------------------------
    button_frame = tk.Frame(search_win, bg="black")
    button_frame.pack(side="right", fill="y", padx=1, pady=5)

    dark_button(button_frame, text="Best", command=find_best).pack(pady=3)
    dark_button(button_frame, text="Top 8", command=show_top).pack(pady=3)
    dark_button(button_frame, text="Copy", command=copy_id).pack(pady=3)
    dark_button(button_frame, text="Clear", command=clear).pack(pady=3)
    dark_button(button_frame, text="Excel", command=open_excel).pack(pady=3)

