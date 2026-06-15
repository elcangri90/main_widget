import tkinter as tk
from tkinter import ttk
import time
import win32com.client as win32

def open_pricing_tool(root, open_windows, close_window):
    key = "pricing_extract"

    # --- If already open → restore + center + bring to front ---
    if key in open_windows:
        kind, win = open_windows[key]
        if kind == "window" and win.winfo_exists():

            if win.state() == "iconic":
                win.state("normal")

            win.update_idletasks()
            w = win.winfo_width()
            h = win.winfo_height()
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            win.geometry(f"{w}x{h}+{x}+{y}")

            win.lift()
            win.focus_force()
            return

    # --- Create window ONCE ---
    pricing_root = tk.Toplevel(root)
    pricing_root.title("Pricing Extract Tool")
    pricing_root.configure(bg="black")
    pricing_root.attributes("-topmost", True)
    pricing_root.resizable(False, False)

    open_windows[key] = ("window", pricing_root)

    # ---------------------------------------------------------
    # START EXCEL (MINIMIZED)
    # ---------------------------------------------------------
    EXCEL_PATH = r'"\\CHNEUPFIL01\Groups\CS\8. Work Instructions\Pricing Search Tool\20220315_Pricing_Search_Tool_ALL_REGIONS_NO_ROWS_LIMITATION.xlsm"'
    SHEET_NAME = "Price List"

    excel = win32.Dispatch("Excel.Application")
    excel.Visible = True
    excel.WindowState = -4140
    excel.DisplayAlerts = False

    wb = excel.Workbooks.Open(EXCEL_PATH, UpdateLinks=0, ReadOnly=False, IgnoreReadOnlyRecommended=True)
    ws = wb.Sheets(SHEET_NAME)

    # ---------------------------------------------------------
    # FUNCTIONS
    # ---------------------------------------------------------
    def run_search():
        cust_id = entry_customer_id.get().strip()
        part_id = entry_part_id.get().strip()

        ws.OLEObjects("CustomerID").Object.Text = cust_id
        ws.OLEObjects("PartID").Object.Text = part_id

        ws.OLEObjects("GetDataButton").Object.Value = True

        time.sleep(0.3)
        excel.CalculateFullRebuild()

        data = ws.Range("I16:L19").Value

        for r in tree.get_children():
            tree.delete(r)

        for row in data:
            cleaned = ["" if v is None else v for v in row]
            tree.insert("", "end", values=cleaned)

    def clear_fields():
        entry_customer_id.delete(0, tk.END)
        entry_part_id.delete(0, tk.END)

        ws.OLEObjects("CustomerID").Object.Text = ""
        ws.OLEObjects("PartID").Object.Text = ""

        ws.Range("I16:L19").ClearContents()
        excel.CalculateFullRebuild()

        for r in tree.get_children():
            tree.delete(r)

    def on_cell_double_click(event):
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = tree.identify_row(event.y)
        col_id = tree.identify_column(event.x)

        if not row_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        values = tree.item(row_id, "values")
        cell_value = values[col_index] if col_index < len(values) else ""

        pricing_root.clipboard_clear()
        pricing_root.clipboard_append(str(cell_value))
        pricing_root.update()

        popup = tk.Label(pricing_root, text="✅", bg="black", fg="lime", font=("Segoe UI", 14))
        popup.place(relx=0.5, rely=0.05, anchor="center")
        pricing_root.after(400, popup.destroy)

    def on_close():
        try: wb.Close(SaveChanges=False)
        except: pass
        try: excel.Quit()
        except: pass
        close_window(key)

    # Center window
    w, h = 485, 150
    sw = pricing_root.winfo_screenwidth()
    sh = pricing_root.winfo_screenheight()
    x = int((sw - w) / 2)
    y = int((sh - h) / 2)
    pricing_root.geometry(f"{w}x{h}+{x}+{y}")

    # Modern dark button
    def dark_button(parent, text, cmd):
        return tk.Button(
            parent,
            text=text,
            command=cmd,
            bg="#2f2f2f",
            fg="white",
            relief="flat",
            activebackground="#3a3a3a",
            activeforeground="white",
            font=("Segoe UI", 8),
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2"
        )

    # Hover effect
    def add_hover(widget, normal="#2f2f2f", hover="#3a3a3a"):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal))

    # Dark Treeview theme
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background="#1e1e1e",
        foreground="white",
        fieldbackground="#1e1e1e",
        bordercolor="#1e1e1e",
        rowheight=22
    )

    style.map(
        "Treeview",
        background=[("selected", "#3a3a3a")],
        foreground=[("selected", "white")]
    )

    # --- Custom isolated Treeview style to prevent header reset ---
    style.configure("Pricing.Treeview",
                    background="#1e1e1e",
                    foreground="white",
                    fieldbackground="#1e1e1e",
                    bordercolor="#1e1e1e",
                    rowheight=22
                    )

    style.map("Pricing.Treeview",
              background=[("selected", "#3a3a3a")],
              foreground=[("selected", "white")]
              )

    style.configure("Pricing.Treeview.Heading",
                    background="#2f2f2f",
                    foreground="white",
                    relief="flat",
                    font=("Segoe UI", 9, "bold")
                    )

    style.map("Pricing.Treeview.Heading",
              background=[("active", "#3a3a3a")],
              foreground=[("active", "white")]
              )

    # ---------------------------------------------------------
    # MAIN LAYOUT
    # ---------------------------------------------------------
    main_frame = tk.Frame(pricing_root, bg="black", highlightbackground="#444", highlightthickness=1)
    main_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # LEFT PANE
    left_pane = tk.Frame(main_frame, bg="black")
    left_pane.pack(side="left", fill="y", padx=(0, 5))

    tk.Label(left_pane, text="ID:", bg="black", fg="white").pack(anchor="w", pady=0)
    entry_customer_id = tk.Entry(left_pane, width=10, bg="gray14", fg="white", insertbackground="white")
    entry_customer_id.pack(anchor="w", pady=0)

    def force_uppercase(event):
        current = entry_customer_id.get()
        entry_customer_id.delete(0, tk.END)
        entry_customer_id.insert(0, current.upper())

    entry_customer_id.bind("<KeyRelease>", force_uppercase)

    tk.Label(left_pane, text="PN:", bg="black", fg="white").pack(anchor="w", pady=0)
    entry_part_id = tk.Entry(left_pane, width=10, bg="gray14", fg="white", insertbackground="white")
    entry_part_id.pack(anchor="w", pady=0)


    # Buttons
    button_row = tk.Frame(left_pane, bg="black")
    button_row.pack(anchor="w", pady=5)

    btn_search = dark_button(button_row, "Search", run_search)
    add_hover(btn_search)
    btn_search.pack(fill="x", pady=(0, 2))

    pricing_root.bind("<Return>", lambda e: run_search())

    btn_clear = dark_button(button_row, "Clear", clear_fields)
    add_hover(btn_clear)
    btn_clear.pack(fill="x", pady=(0, 2))

    pricing_root.bind("<Escape>", lambda e: clear_fields())

    # RIGHT PANE
    right_pane = tk.LabelFrame(main_frame, bg="black", fg="white")
    right_pane.pack(side="left", fill="both", expand=True)

    columns = ("I", "J", "K", "L")
    tree = ttk.Treeview(right_pane,columns=columns,show="headings",height=10,style="Pricing.Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    tree.bind("<Double-1>", on_cell_double_click)

    vsb = ttk.Scrollbar(right_pane, orient="vertical", command=tree.yview)
    tree.configure(yscroll=vsb.set)

    tree.pack(side="left", fill="both", expand=False)
    vsb.pack(side="right", fill="y")

    pricing_root.protocol("WM_DELETE_WINDOW", on_close)
