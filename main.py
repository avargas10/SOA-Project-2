import tkinter as tk
from gui_interface import gui

def main():
    root = tk.Tk()
    root.title("Task Scheduler GUI")
    app = gui(root)  # Initialize the GUI with the root window
    root.mainloop()  # Start the GUI event loop

if __name__ == "__main__":
    main()