import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

class TaskEditor(tk.Toplevel):
    def __init__(self, master, csv_path="tasks.csv"):
        super().__init__(master)
        self.title("Task list")
        self.geometry("650x300")
        self.attributes("-topmost", True)
        self.csv_path = csv_path

        # --- Treeview with 4 columns ---
        self.tree = ttk.Treeview(
            self,
            columns=("date", "so", "po", "task"),
            show="headings"
        )

        self.tree.heading("date", text="Date")
        self.tree.heading("so", text="SO")
        self.tree.heading("po", text="PO")
        self.tree.heading("task", text="Task")

        self.tree.column("date", width=60)
        self.tree.column("so", width=60)
        self.tree.column("po", width=60)
        self.tree.column("task", width=300)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Buttons (horizontal) ---
        # --- Buttons (horizontal) ---
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        add_btn = tk.Button(button_frame, text="Add New Task", command=self.add_task_popup)
        add_btn.pack(side="left", padx=5)

        del_btn = tk.Button(button_frame, text="Delete Selected", command=self.delete_task)
        del_btn.pack(side="left", padx=5)

        edit_btn = tk.Button(button_frame, text="Edit Selected", command=self.edit_task)
        edit_btn.pack(side="left", padx=5)

        save_btn = tk.Button(button_frame, text="Save to CSV", command=self.save_csv)
        save_btn.pack(side="left", padx=5)

        # Load existing tasks
        self.load_csv()

    # ---------------- Helper: center any window ---------------- #

    def center_window(self, win, w, h):
        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    # ---------------- CSV Logic ---------------- #

    def load_csv(self):
        if not os.path.exists(self.csv_path):
            return
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) == 4:
                    self.tree.insert("", "end", values=row)

    def save_csv(self):
        rows = [
            self.tree.item(i)["values"]
            for i in self.tree.get_children()
        ]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)
        messagebox.showinfo("Saved", "Tasks saved successfully.")

    # ---------------- Add Task (Popup) ---------------- #

    def add_task_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add New Task")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)

        # set size then center
        w, h = 400, 250
        popup.geometry(f"{w}x{h}")
        self.center_window(popup, w, h)

        fields = ["Date", "SO", "PO", "Task"]
        entries = []

        for label in fields:
            tk.Label(popup, text=label).pack(pady=3)
            e = tk.Entry(popup, width=40)
            e.pack()
            entries.append(e)

        def save_new_task():
            values = [e.get().strip() for e in entries]
            if all(values):
                self.tree.insert("", "end", values=values)
                popup.destroy()
            else:
                messagebox.showwarning("Missing data", "All fields are required.")

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", command=save_new_task).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=5)

    # ---------------- Delete Task ---------------- #

    def delete_task(self):
        selected = self.tree.selection()
        for item in selected:
            self.tree.delete(item)

    # ---------------- Edit Task ---------------- #

    def edit_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a task to edit.")
            return

        item = selected[0]
        old_date, old_so, old_po, old_task = self.tree.item(item, "values")

        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Task")
        edit_win.resizable(False, False)
        edit_win.attributes("-topmost", True)

        w, h = 400, 250
        edit_win.geometry(f"{w}x{h}")
        self.center_window(edit_win, w, h)

        fields = ["Date", "SO", "PO", "Task"]
        old_values = [old_date, old_so, old_po, old_task]
        entries = []

        for i, label in enumerate(fields):
            tk.Label(edit_win, text=label).pack(pady=3)
            e = tk.Entry(edit_win, width=40)
            e.pack()
            e.insert(0, old_values[i])
            entries.append(e)

        def save_changes():
            new_values = [e.get().strip() for e in entries]
            if all(new_values):
                self.tree.item(item, values=new_values)
                edit_win.destroy()
            else:
                messagebox.showwarning("Missing data", "All fields are required.")

        btn_frame = tk.Frame(edit_win)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Save", command=save_changes).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=edit_win.destroy).pack(side="left", padx=5)
