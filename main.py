import tkinter as tk

from Display import gui

root = tk.Tk()
root.title("Option Chain Live Moniter")
a = gui.Display(root)
a.pack(side="top", fill="both", expand=True)
a.refresh()

root.mainloop()