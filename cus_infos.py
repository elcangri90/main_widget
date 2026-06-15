import tkinter as tk
import sqlite3
import json
import webbrowser
import re
import subprocess
import os
import sys

# ---------------------------------------------------------
# 1. Save JSON → SQLite (REFRESH DB)
# ---------------------------------------------------------
def save_document(db_path, json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            json_content TEXT NOT NULL
        )
    """)

    cur.execute("""
        UPDATE documents
        SET title = ?, json_content = ?
        WHERE document_id = ?
    """, (
        data["title"],
        json.dumps(data, indent=2),
        data["document_id"]
    ))

    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO documents (document_id, title, json_content)
            VALUES (?, ?, ?)
        """, (
            data["document_id"],
            data["title"],
            json.dumps(data, indent=2)
        ))

    conn.commit()
    conn.close()



# ---------------------------------------------------------
# 2. Load JSON from SQLite
# ---------------------------------------------------------
def load_document_by_id(db_path, document_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT json_content
        FROM documents
        WHERE document_id = ?
        LIMIT 1
    """, (document_id,))

    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return json.loads(row[0])



# ---------------------------------------------------------
# 3. Open the CUS Viewer window
# ---------------------------------------------------------
def open_cus_viewer(root, open_windows, close_window):
    key = "cus_infos"

    if key in open_windows:
        kind, win = open_windows[key]
        if kind == "window" and win.winfo_exists():
            if win.state() == "iconic":
                win.state("normal")
            win.lift()
            win.focus_force()
            return

    win = tk.Toplevel(root)
    win.title("CUS Viewer")
    win.configure(bg="black")
    win.geometry("900x600")
    win.attributes("-topmost", False)

    open_windows[key] = ("window", win)
    win.protocol("WM_DELETE_WINDOW", lambda: close_window(key))

    # LEFT SIDE
    left = tk.Frame(win, bg="black")
    left.pack(side="left", fill="y", padx=10, pady=10)

    tk.Label(left, text="Sections", fg="white", bg="black").pack(anchor="w")

    section_list = tk.Listbox(left, width=30, height=30, bg="#1e1e1e", fg="white")
    section_list.pack(fill="y")

    def close_on_esc(event=None):
        win.destroy()
        return "break"
    win.bind("<Escape>", lambda event: close_on_esc())


    # RIGHT SIDE
    right = tk.Frame(win, bg="black")
    right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # SEARCH BAR
    search_frame = tk.Frame(right, bg="black")
    search_frame.pack(fill="x", anchor="ne")

    search_entry = tk.Entry(search_frame, width=25)
    search_entry.pack(side="right", padx=5, pady=5)

    def focus_search(event=None):
        search_entry.focus_set()
        search_entry.select_range(0, 'end')
        return "break"

    win.bind("<Control-f>", focus_search)
    win.bind("<Control-F>", focus_search)

    URL_REGEX = re.compile(r"https?://[^\s]+")

    def is_url(text):
        return URL_REGEX.match(text) is not None

    def is_local_file(path):
        if re.match(r"^[A-Za-z]:\\", path):
            return True
        if path.startswith("\\\\"):
            return True
        if path.startswith("./") or path.startswith("../"):
            return True
        return False

    def open_local_file(path):
        try:
            if os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.call(("open" if sys.platform == "darwin" else "xdg-open", path))
        except Exception as e:
            print("Error opening file:", e)

    def do_search():
        text.tag_remove("highlight", "1.0", "end")
        query = search_entry.get()

        if not query:
            return

        start = "1.0"
        while True:
            pos = text.search(query, start, stopindex="end", nocase=True)
            if not pos:
                break

            end = f"{pos}+{len(query)}c"
            text.tag_add("highlight", pos, end)
            start = end

        text.tag_config("highlight", background="yellow", foreground="black")

    search_entry.bind("<Return>", lambda event: do_search())


    # MAIN TEXT
    text = tk.Text(
        right, bg="#1e1e1e", fg="white",
        insertbackground="white", wrap="word",
        font=("Calibri", 11), height=25
    )
    text.pack(fill="both", expand=True)

    # Load JSON
    doc = load_document_by_id("docs.db", "CUS_infos")

    if not doc:
        text.insert("end", "Document not found in database.")
        return

    # Fill list
    for sec in doc["sections"]:
        section_list.insert("end", sec["name"])


    # ---------------------------------------------------------
    # SHOW SECTION (FIXED)
    # ---------------------------------------------------------
    def show_section(event):
        selection = section_list.curselection()
        if not selection:
            return

        index = selection[0]
        section = doc["sections"][index]

        text.delete("1.0", "end")
        text.insert("end", f"{section['name']}\n")
        text.insert("end", "-" * 40 + "\n\n")

        for i, line in enumerate(section["data"]):
            tag_name = f"link_{i}"

            # Insert the line first
            text.insert("end", line + "\n")

            # Get the start of the line just inserted
            line_start = text.index(f"end - {len(line) + 1}c")
            line_end = f"{line_start}+{len(line)}c"

            # --- URL WEB ---
            if is_url(line):
                text.tag_add(tag_name, line_start, line_end)
                text.tag_config(tag_name, foreground="cyan", underline=True)

                text.tag_bind(tag_name, "<Enter>", lambda e: text.config(cursor="hand2"))
                text.tag_bind(tag_name, "<Leave>", lambda e: text.config(cursor=""))
                text.tag_bind(tag_name, "<Button-1>", lambda e, url=line: webbrowser.open(url))

            # --- LOCAL FILE ---
            elif is_local_file(line):
                text.tag_add(tag_name, line_start, line_end)
                text.tag_config(tag_name, foreground="lightgreen", underline=True)

                text.tag_bind(tag_name, "<Enter>", lambda e: text.config(cursor="hand2"))
                text.tag_bind(tag_name, "<Leave>", lambda e: text.config(cursor=""))
                text.tag_bind(tag_name, "<Button-1>", lambda e, path=line: open_local_file(path))

            # --- NORMAL TEXT ---
            else:
                pass  # already inserted above

        # Clear highlights when switching sections
        text.tag_remove("highlight", "1.0", "end")

    section_list.bind("<<ListboxSelect>>", show_section)
