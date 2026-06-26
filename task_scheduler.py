# task_scheduler.py

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk

TASKS_FILE = "task_file.json"

# ------------------------------
# Load & Save
# ------------------------------
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# ------------------------------
# Background Scheduler (ONE BLOCK)
# ------------------------------
def scheduler_loop(root, ACTIONS):
    tasks = load_tasks()
    now = datetime.now().strftime("%H:%M")

    for name, t in tasks.items():
        if not t.get("enabled", True):
            continue

        if t["time"] == now:
            action = t["action"]
            if action in ACTIONS:
                try:
                    ACTIONS[action]()
                    t["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    save_tasks(tasks)
                except Exception as e:
                    print(f"Task '{name}' failed:", e)

    # reschedule
    root.after(30000, lambda: scheduler_loop(root, ACTIONS))

def start_scheduler(root, ACTIONS):
    root.after(1000, lambda: scheduler_loop(root, ACTIONS))

# ------------------------------
# Scheduler Window (ONE BLOCK)
# ------------------------------
def open_task_scheduler(root, open_windows, close_window):

    key = "task_scheduler"

    # Prevent duplicates
    if key in open_windows:
        kind, win = open_windows[key]
        if win.winfo_exists():
            win.lift()
            return
        else:
            del open_windows[key]

    win = tk.Toplevel(root)
    win.title("Task Scheduler")
    win.attributes("-topmost", True)
    win.configure(bg="black")
    win.resizable(False, False)

    open_windows[key] = ("window", win)

    tasks = load_tasks()

    frame = ttk.Frame(win)
    frame.pack(padx=10, pady=10)

    tree = ttk.Treeview(frame, columns=("time", "action", "enabled"), show="headings")
    tree.heading("time", text="Time")
    tree.heading("action", text="Action")
    tree.heading("enabled", text="Enabled")

    for name, t in tasks.items():
        tree.insert("", "end", iid=name, values=(t["time"], t["action"], t.get("enabled", True)))

    tree.pack()

    # Add Task
    def add_task():
        add_win = tk.Toplevel(win)
        add_win.title("Add Task")
        add_win.attributes("-topmost", True)
        add_win.configure(bg="black")

        tk.Label(add_win, text="Time (HH:MM)", bg="black", fg="white").pack()
        time_entry = tk.Entry(add_win)
        time_entry.pack()

        tk.Label(add_win, text="Action", bg="black", fg="white").pack()
        action_entry = tk.Entry(add_win)
        action_entry.pack()

        def save_new():
            name = f"task_{len(tasks)+1}"
            tasks[name] = {
                "time": time_entry.get(),
                "action": action_entry.get(),
                "enabled": True
            }
            save_tasks(tasks)
            tree.insert("", "end", iid=name, values=(tasks[name]["time"], tasks[name]["action"], True))
            add_win.destroy()

        tk.Button(add_win, text="Save", command=save_new).pack(pady=5)

    tk.Button(win, text="Add Task", command=add_task).pack(pady=5)

    # Close on ESC
    def close_on_esc(event=None):
        close_window(key)
        return "break"

    win.bind("<Escape>", close_on_esc)
