import tkinter as tk
from tkinter import messagebox
import logging
from instrument.gilson import gsioc_protocol, direct_injection_module
from instrument.platform_setup import gx241_com_port, gx241_ID, dim_ID, baudrate, rack1_commands, hplc_vial
from spka import spka

class SPKA_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SPKA Protocol Runner")
        
        # Logging setup
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        # Initialize platform
        self.gx241, self.dim = None, None
        self.initialize_platform()

        # Create input fields and buttons
        self.create_widgets()

        # Create rack window
        self.create_rack_window()

    def initialize_platform(self):
        try:
            self.gx241, self.dim = initialize_platform()
            messagebox.showinfo("Info", "Platform initialized successfully.")
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            messagebox.showerror("Error", f"Initialization error: {e}")

    def create_widgets(self):
        # Labels and Entry fields for the numbers
        tk.Label(self.root, text="Number of Cat").grid(row=0, column=0)
        self.cat_entry = tk.Entry(self.root)
        self.cat_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Number of Sub B").grid(row=1, column=0)
        self.sub_b_entry = tk.Entry(self.root)
        self.sub_b_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Number of Sub A").grid(row=2, column=0)
        self.sub_a_entry = tk.Entry(self.root)
        self.sub_a_entry.grid(row=2, column=1)

        # Run button
        self.run_button = tk.Button(self.root, text="Run SPKA", command=self.run_spka)
        self.run_button.grid(row=3, column=0, columnspan=2)

    def create_rack_window(self):
        self.rack_window = tk.Toplevel(self.root)
        self.rack_window.title("Rack Layout")
        self.canvas = tk.Canvas(self.rack_window, width=200, height=400)
        self.canvas.pack()
        self.draw_rack()

    def draw_rack(self):
        self.vial_circles = []
        for row in range(16):  # 16 rows
            for col in range(4):  # 4 columns
                x0 = 10 + col * 25  # Halve the size
                y0 = 10 + row * 25  # Halve the size
                x1 = x0 + 20  # Halve the size
                y1 = y0 + 20  # Halve the size
                circle = self.canvas.create_oval(x0, y0, x1, y1, outline="black", fill="white")
                self.vial_circles.append((circle, col))

    def update_vials(self, no_sub_a, no_sub_b, no_cat):
        self.logger.debug(f"Updating vials: no_sub_a={no_sub_a}, no_sub_b={no_sub_b}, no_cat={no_cat}")
        for i, (circle, col) in enumerate(self.vial_circles):
            if col == 0 and no_sub_a > 0:
                self.canvas.itemconfig(circle, fill="red")
                no_sub_a -= 1
            elif col == 1 and no_sub_b > 0:
                self.canvas.itemconfig(circle, fill="green")
                no_sub_b -= 1
            elif col == 2 and no_cat > 0:
                self.canvas.itemconfig(circle, fill="blue")
                no_cat -= 1
            else:
                self.canvas.itemconfig(circle, fill="white")
        self.rack_window.update_idletasks()

    def run_spka(self):
        try:
            # Read and process input numbers
            no_cat = int(self.cat_entry.get())
            no_sub_b = int(self.sub_b_entry.get())
            no_sub_a = int(self.sub_a_entry.get())

            # Log the input values
            self.logger.debug(f"Inputs - no_cat: {no_cat}, no_sub_b: {no_sub_b}, no_sub_a: {no_sub_a}")

            # Generate SPKA combinations
            combinations = spka.generate_combinations([no_cat], [no_sub_b], [no_sub_a])

            # Run SPKA standard procedure
            spka.spka_standard(self.gx241, self.dim, combinations)

            # Update rack display
            self.update_vials(no_sub_a, no_sub_b, no_cat)

            messagebox.showinfo("Info", "SPKA procedure completed successfully.")
        
        except Exception as e:
            self.logger.error(f"Error during SPKA run: {e}")
            messagebox.showerror("Error", f"Error during SPKA run: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SPKA_GUI(root)
    root.mainloop()
