import tkinter as tk
from tkinter import ttk
import requests

def open_calculator(root, open_windows, close_window):
    key = "Calculator"

    # --- If already open ---
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

    # --- Create calculator window ---
    calc = tk.Toplevel(root)
    calc.title("Calculator")
    calc.resizable(False, False)
    calc.attributes("-topmost", True)
    calc.configure(bg="#1e1e1e")

    open_windows[key] = ("window", calc)

    calc.protocol("WM_DELETE_WINDOW", lambda: close_window(key))
    calc.bind("<Escape>", lambda e: close_window(key))

    # --- Expression display ---
    expr_display = tk.Entry(
        calc,
        font=("Roboto", 12),
        borderwidth=0,
        relief="flat",
        justify="right",
        bg="#1e1e1e",
        fg="#bbbbbb",
        highlightthickness=0
    )
    expr_display.pack(fill="both", padx=12, pady=(12, 0))

    # --- Main display ---
    display = tk.Entry(
        calc,
        font=("Roboto", 18),
        borderwidth=0,
        relief="flat",
        justify="right",
        bg="#2d2d2d",
        fg="white",
        insertbackground="white",
        highlightthickness=0
    )
    display.pack(fill="both", padx=12, pady=4, ipady=10)

    # Center window
    calc.update_idletasks()
    w = calc.winfo_width()
    h = calc.winfo_height()
    sw = calc.winfo_screenwidth()
    sh = calc.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    calc.geometry(f"{w}x{h}+{x}+{y}")
    calc.geometry("250x320")

    # --- Calculator state ---
    current_value = 0.0
    current_operator = None
    reset_display = False

    def apply_operation(value, operator, new_value):
        if operator == "+":
            return value + new_value
        elif operator == "-":
            return value - new_value
        elif operator == "*":
            return value * new_value
        elif operator == "/":
            return value / new_value if new_value != 0 else float("inf")
        return new_value

    def on_click(value):
        nonlocal current_value, current_operator, reset_display

        if value.isdigit():
            if reset_display:
                display.delete(0, tk.END)
                reset_display = False
            display.insert(tk.END, value)

        elif value in ["+", "-", "*", "/"]:
            new_number = float(display.get()) if display.get() else 0

            if current_operator is None:
                current_value = new_number
            else:
                current_value = apply_operation(current_value, current_operator, new_number)

            current_operator = value

            expr_display.delete(0, tk.END)
            expr_display.insert(0, f"{current_value} {value}")

            display.delete(0, tk.END)
            display.insert(0, f"{current_value:.2f}")

            reset_display = True

        elif value == "=":
            new_number = float(display.get()) if display.get() else 0

            if current_operator is not None:
                expr_display.delete(0, tk.END)
                expr_display.insert(0, f"{current_value} {current_operator} {new_number}")

                current_value = apply_operation(current_value, current_operator, new_number)

            display.delete(0, tk.END)
            display.insert(0, f"{current_value:.2f}")


            current_operator = None
            reset_display = True

        elif value == "C":
            current_value = 0.0
            current_operator = None
            reset_display = False
            display.delete(0, tk.END)
            expr_display.delete(0, tk.END)

        elif value == "DEL":
            display.delete(len(display.get()) - 1, tk.END)

    # --- Keyboard support ---
    def on_key(event):
        key = event.keysym

        if key in "0123456789":
            on_click(key)
            return "break"
        elif key in ["plus", "KP_Add"]:
            on_click("+")
            return "break"
        elif key in ["minus", "KP_Subtract"]:
            on_click("-")
            return "break"
        elif key in ["asterisk", "KP_Multiply"]:
            on_click("*")
            return "break"
        elif key in ["slash", "KP_Divide"]:
            on_click("/")
            return "break"
        elif key == "Return":
            on_click("=")
            return "break"
        elif key == "BackSpace":
            on_click("DEL")
            return "break"
        elif key == "Escape":
            on_click("C")
            return "break"

    display.bind("<Key>", on_key)

    # --- Calculator buttons ---
    # --- Local ttk style for calculator buttons ---
    style = ttk.Style(calc)
    style.theme_use("clam")  # isolates from other windows

    style.configure(
        "Modern.TButton",
        font=("Roboto", 10),
        padding=6,
        background="#3a3a3a",
        foreground="white",
        borderwidth=0
    )

    style.map(
        "Modern.TButton",
        background=[("active", "#505050")],
        foreground=[("active", "white")]
    )

    # --- Calculator buttons ---
    buttons = [
        "7", "8", "9", "/",
        "4", "5", "6", "*",
        "1", "2", "3", "-",
        "C", "0", "=", "+"
    ]

    frame = tk.Frame(calc, bg="#1e1e1e")
    frame.pack()

    row = 0
    col = 0

    for button in buttons:
        b = ttk.Button(
            frame,
            text=button,
            style="Modern.TButton",
            width=4,
            command=lambda x=button: on_click(x)
        )
        b.grid(row=row, column=col, padx=4, pady=4)

        col += 1
        if col > 3:
            col = 0
            row += 1

    # --- Currency conversion integration ---
    def get_rate(from_currency, to_currency):
        url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
        response = requests.get(url)
        data = response.json()
        return data["rates"][to_currency]

    def convert_currency(from_cur, to_cur):
        try:
            amount = float(display.get())
            rate = get_rate(from_cur, to_cur)
            result = amount * rate

            display.delete(0, tk.END)
            display.insert(0, f"{result:.2f}")

            expr_display.delete(0, tk.END)
            expr_display.insert(0, f"{amount} {from_cur} → {to_cur}")

        except:
            display.delete(0, tk.END)
            display.insert(0, "ERR")

    # --- Conversion buttons ---
    # --- Conversion buttons (EUR ↔ USD only) ---
    conv_frame = tk.Frame(calc, bg="#1e1e1e")
    conv_frame.pack(pady=4)

    ttk.Button(
        conv_frame, text="USD → EUR",
        style="Modern.TButton",
        command=lambda: convert_currency("USD", "EUR")
    ).grid(row=0, column=0, padx=4, pady=4)

    ttk.Button(
        conv_frame, text="EUR → USD",
        style="Modern.TButton",
        command=lambda: convert_currency("EUR", "USD")
    ).grid(row=0, column=1, padx=4, pady=4)

    # Close on space
    def close_on_space(event=None):
        calc.destroy()
        return "break"

    calc.bind("<KeyPress-space>", close_on_space)
