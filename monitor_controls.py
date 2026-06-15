from monitorcontrol import get_monitors
import tkinter as tk

def open_monitor_controls(root, open_windows, close_window):
    key = "monitor_controls"

    # Prevent multiple instances
    if key in open_windows:
        kind, win = open_windows[key]
        if kind == "window" and win.winfo_exists():
            win.lift()
            win.focus_force()
            return

    # Window
    win = tk.Toplevel(root)
    win.attributes("-topmost", True)
    win.resizable(False, False)
    win.configure(bg="black")

    # Center window
    w, h = 220, 220
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    # Register window
    open_windows[key] = ("window", win)
    win.protocol("WM_DELETE_WINDOW", lambda: close_window(key))
    win.bind("<Escape>", lambda e: close_window(key))

    # ---------------------------------------------------------
    # Modern dark button
    # ---------------------------------------------------------
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
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )

    # Hover effect
    def add_hover(widget, normal="#2f2f2f", hover="#3a3a3a"):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal))

    # ---------------------------------------------------------
    # Title
    # ---------------------------------------------------------
    tk.Label(
        win,
        bg="black",
        fg="white",
        font=("Segoe UI Semibold", 13)
    ).pack(pady=8)

    # ---------------------------------------------------------
    # Monitor detection
    # ---------------------------------------------------------
    monitors = get_monitors()

    def get_avg_luminance():
        vals = []
        for m in monitors:
            try:
                with m:
                    vals.append(m.get_luminance())
            except:
                pass
        return sum(vals) // len(vals) if vals else 50

    def get_avg_contrast():
        vals = []
        for m in monitors:
            try:
                with m:
                    vals.append(m.get_contrast())
            except:
                pass
        return sum(vals) // len(vals) if vals else 50

    # ---------------------------------------------------------
    # Sliders (modern dark style)
    # ---------------------------------------------------------
    slider_style = {
        "fg": "white",
        "bg": "black",
        "troughcolor": "#1e1e1e",
        "highlightthickness": 0,
        "font": ("Segoe UI", 8),
        "length": 200
    }

    bright = tk.Scale(
        win, from_=0, to=100, orient="horizontal",
        label="Brightness", **slider_style
    )
    bright.pack(pady=10)
    bright.set(get_avg_luminance())

    contrast = tk.Scale(
        win, from_=0, to=100, orient="horizontal",
        label="Contrast", **slider_style
    )
    contrast.pack(pady=10)
    contrast.set(get_avg_contrast())

    # ---------------------------------------------------------
    # Update functions
    # ---------------------------------------------------------
    def update_brightness(val):
        for m in monitors:
            try:
                with m:
                    m.set_luminance(int(float(val)))
            except:
                pass

    def update_contrast(val):
        for m in monitors:
            try:
                with m:
                    m.set_contrast(int(float(val)))
            except:
                pass

    bright.configure(command=update_brightness)
    contrast.configure(command=update_contrast)

    # ---------------------------------------------------------
    # Reset button
    # ---------------------------------------------------------
    btn_reset = dark_button(win, "Reset", lambda: [
        bright.set(get_avg_luminance()),
        contrast.set(get_avg_contrast())
    ])
    add_hover(btn_reset)
    btn_reset.pack(pady=5)
