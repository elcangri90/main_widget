def restore_minimized_windows(root, open_windows):
    for name, (kind, win) in open_windows.items():
        if kind != "window":
            continue
        if win is root:
            continue
        if win.winfo_exists() and win.state() == "iconic":
            try:
                win.state("normal")
                win.lift()
            except:
                pass
