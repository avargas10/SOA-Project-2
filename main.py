import tkinter as tk
from gui_interface import gui
from cli_interface import cli

def main():
    def run_gui():
        global choice
        choice = 'gui'
        window.quit()

    def run_cli():
        global choice
        choice = 'cli'
        window.quit()

    window = tk.Tk()
    window.title("Choose Interface")

    label = tk.Label(window, text="Select the interface to run:")
    label.pack(pady=10)

    gui_button = tk.Button(window, text="GUI", command=run_gui)
    cli_button = tk.Button(window, text="CLI", command=run_cli)
    gui_button.pack(side=tk.LEFT, padx=10, pady=20)
    cli_button.pack(side=tk.RIGHT, padx=10, pady=20)

    window.mainloop()
    window.destroy()

    if choice == 'gui':
        root = tk.Tk()
        app = gui(root)  # Pass only the root to gui
        root.mainloop()
    elif choice == 'cli':
        cli_handler = cli()
        cli_handler.run()

if __name__ == "__main__":
    main()
