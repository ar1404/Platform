import tkinter as tk
from tkinter import font, messagebox
from spka import spka

class InteractiveRack:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Rack")

        # Constants for sizes and layout
        self.circle_diameter = 20
        self.num_rows = 16
        self.num_cols = 4

        # Calculate inner padding for even distribution
        inner_padding_x = self.circle_diameter / 2
        inner_padding_y = self.circle_diameter / 2

        # Calculate canvas size
        self.rect_padding = inner_padding_x / 2
        self.left_padding = 50  # Additional padding for row numbers
        self.right_padding = 350  # Additional padding for controls on the right

        # Dynamic canvas width to accommodate the extra text and text boxes
        self.control_width = 350
        self.canvas_width = self.num_cols * (self.circle_diameter + inner_padding_x) + 2 * self.rect_padding + self.left_padding + self.control_width
        self.canvas_height = self.num_rows * (self.circle_diameter + inner_padding_y) + 2 * self.rect_padding + self.circle_diameter * 3 + inner_padding_y

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Variables to keep track of the number of selected vials in each column
        self.num_sub_a = 0
        self.num_sub_b = 0
        self.num_cat = 0
        self.num_additive = 0

        # Variables for user inputs with default values
        self.no_spka_points = tk.IntVar(value=4)
        self.spka_conv = tk.IntVar(value=20)
        self.t0 = tk.BooleanVar(value=True)
        self.order_in_A_B = tk.BooleanVar(value=True)
        self.order_in_cat = tk.BooleanVar(value=True)
        self.vol_sub_A = tk.DoubleVar(value=0.1)
        self.vol_sub_B = tk.DoubleVar(value=0.1)
        self.vol_cat = tk.DoubleVar(value=0.01)
        self.A0 = tk.DoubleVar(value=0.1)
        self.B0_stand = tk.DoubleVar(value=0.15)
        self.B0_DE = tk.DoubleVar(value=0.1)
        self.C0_stand = tk.DoubleVar(value=0.01)
        self.C0_DE = tk.DoubleVar(value=0.02)

        # Store inner padding for later use
        self.inner_padding_x = inner_padding_x
        self.inner_padding_y = inner_padding_y

        # Draw the rack
        self.draw_rack()

        # Create additional controls
        self.create_controls()

    def draw_rack(self):
        self.vial_circles = {}
        colors = ['red', 'green', 'blue', 'yellow']
        variable_names = ['Substrate A', 'Substrate B', 'Catalyst', 'Additive']

        # Calculate top left corner of the rack
        rack_top_left_x = self.left_padding
        rack_top_left_y = self.rect_padding * 8 + self.circle_diameter

        # Draw the rectangle around the rack
        self.canvas.create_rectangle(
            rack_top_left_x - self.rect_padding,
            rack_top_left_y - self.rect_padding,
            rack_top_left_x + self.num_cols * (self.circle_diameter + self.inner_padding_x) - self.inner_padding_x + self.rect_padding,
            rack_top_left_y + self.num_rows * (self.circle_diameter + self.inner_padding_y) - self.inner_padding_y + self.rect_padding,
            outline="black"
        )

        # Draw the circles and row numbers
        for row in range(self.num_rows):
            # Row numbers aligned with the centers of the circles
            self.canvas.create_text(
                rack_top_left_x - self.rect_padding * 2,
                rack_top_left_y + row * (self.circle_diameter + self.inner_padding_y) + self.circle_diameter / 2,
                text=str(row + 1),
                anchor="e"
            )

            for col in range(self.num_cols):
                x0 = rack_top_left_x + col * (self.circle_diameter + self.inner_padding_x)
                y0 = rack_top_left_y + row * (self.circle_diameter + self.inner_padding_y)
                x1 = x0 + self.circle_diameter
                y1 = y0 + self.circle_diameter
                circle = self.canvas.create_oval(x0, y0, x1, y1, outline="black", fill="white")
                self.vial_circles[(row, col)] = circle
                self.canvas.tag_bind(circle, '<Button-1>', lambda event, r=row, c=col: self.fill_circles(r, c, colors[c]))

        # Column headers rotated by 45 degrees
        for col in range(self.num_cols):
            self.canvas.create_text(
                rack_top_left_x + col * (self.circle_diameter + self.inner_padding_x) + self.circle_diameter,
                rack_top_left_y - self.rect_padding * 6,
                text=variable_names[col],
                angle=45,
                anchor="center"
            )

        # Column footers for displaying counts, a circle diameter below the last row
        self.count_texts = []
        for col in range(self.num_cols):
            count_text = self.canvas.create_text(
                rack_top_left_x + col * (self.circle_diameter + self.inner_padding_x) + self.circle_diameter / 2,
                rack_top_left_y + self.num_rows * (self.circle_diameter + self.inner_padding_y) + self.rect_padding,
                text="0",
                anchor="center"
            )
            self.count_texts.append(count_text)

    def create_controls(self):
        control_x = self.canvas_width - self.control_width + 10
        control_y = 50
        control_spacing = 30

        # Label and entry for SPKA points
        tk.Label(self.root, text="Number of SPKA points:").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.no_spka_points).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Label and entry for SPKA Conversion
        tk.Label(self.root, text="SPKA Conversion:").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.spka_conv).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Checkbox for t0
        tk.Checkbutton(self.root, text="t0", variable=self.t0).place(x=control_x, y=control_y)
        control_y += control_spacing

        # Checkbox for Order in A and B
        tk.Checkbutton(self.root, text="Order in A and B", variable=self.order_in_A_B).place(x=control_x, y=control_y)
        control_y += control_spacing

        # Checkbox for Order in Catalyst
        tk.Checkbutton(self.root, text="Order in Catalyst", variable=self.order_in_cat).place(x=control_x, y=control_y)
        control_y += control_spacing

        # Label and entry for Volume of Sub A
        tk.Label(self.root, text="Volume of Sub A (mL):").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.vol_sub_A).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Label and entry for Volume of Sub B
        tk.Label(self.root, text="Volume of Sub B (mL):").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.vol_sub_B).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Label and entry for Volume of Catalyst
        tk.Label(self.root, text="Volume of Catalyst (mL):").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.vol_cat).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Label and entry for A0
        tk.Label(self.root, text="A0 (M):").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.A0).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Label and entry for B0_stand
        tk.Label(self.root, text="B0_stand (M):").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.B0_stand).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Label and entry for B0_DE
        tk.Label(self.root, text="B0_DE (M):").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.B0_DE).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Label and entry for C0_stand
        tk.Label(self.root, text="C0_stand (M):").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.C0_stand).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Label and entry for C0_DE
        tk.Label(self.root, text="C0_DE (M):").place(x=control_x, y=control_y)
        tk.Entry(self.root, textvariable=self.C0_DE).place(x=control_x + 150, y=control_y)

        control_y += control_spacing

        # Button to instantiate SPKA class
        tk.Button(self.root, text="Run SPKA", command=self.run_spka).place(x=control_x, y=control_y + control_spacing)
        tk.Button(self.root, text="Check SPKA", command=self.check_spka).place(x=control_x, y=control_y + 2 * control_spacing)

    def fill_circles(self, row, col, color):
        # Reset all circles in the column to white
        for r in range(self.num_rows):
            self.canvas.itemconfig(self.vial_circles[(r, col)], fill="white")
        
        # Fill circles up to the selected row with the specified color
        for r in range(row + 1):
            self.canvas.itemconfig(self.vial_circles[(r, col)], fill=color)
        
        # Update the count variables and display the count
        if col == 0:
            self.num_sub_a = row + 1
            self.canvas.itemconfig(self.count_texts[col], text=str(self.num_sub_a))
        elif col == 1:
            self.num_sub_b = row + 1
            self.canvas.itemconfig(self.count_texts[col], text=str(self.num_sub_b))
        elif col == 2:
            self.num_cat = row + 1
            self.canvas.itemconfig(self.count_texts[col], text=str(self.num_cat))
        elif col == 3:
            self.num_additive = row + 1
            self.canvas.itemconfig(self.count_texts[col], text=str(self.num_additive))

        # Print the updated counts
        print(f"Substrate A: {self.num_sub_a}")
        print(f"Substrate B: {self.num_sub_b}")
        print(f"Catalyst: {self.num_cat}")
        print(f"Additive: {self.num_additive}")

    def run_spka(self):
        # Instantiate the SPKA class with variables from the GUI
        spka_experiment = spka(
            no_sub_A=self.num_sub_a,
            no_sub_B=self.num_sub_b,
            no_cat=self.num_cat,
            no_spka_points=self.no_spka_points.get(),
            spka_conv=self.spka_conv.get(),
            t0=self.t0.get(),
            order_in_A_B=self.order_in_A_B.get(),
            order_in_cat=self.order_in_cat.get()
        )

        # Call the spka_volumes method and get the result
        spka_combinations = spka_experiment.spka_combinations()
        spka_volumes, volume_dict = spka_experiment.spka_volumes(
            vol_sub_A=self.vol_sub_A.get(),
            vol_sub_B=self.vol_sub_B.get(),
            vol_cat=self.vol_cat.get(),
            A0=self.A0.get(),
            B0_stand=self.B0_stand.get(),
            B0_DE=self.B0_DE.get(),
            C0_Stand=self.C0_stand.get(),
            C0_DE=self.C0_DE.get()
        )

        # Print the results (optional)
        print("SPKA Combinations:", spka_combinations)
        print("SPKA Volumes:", spka_volumes)
        print("Volume Dictionary:", volume_dict)

    def check_spka(self):
        # Instantiate the SPKA class with variables from the GUI
        spka_experiment = spka(
            no_sub_A=self.num_sub_a,
            no_sub_B=self.num_sub_b,
            no_cat=self.num_cat,
            no_spka_points=self.no_spka_points.get(),
            spka_conv=self.spka_conv.get(),
            t0=self.t0.get(),
            order_in_A_B=self.order_in_A_B.get(),
            order_in_cat=self.order_in_cat.get()
        )

        # Call the spka_volumes method and get the result
        spka_combinations = spka_experiment.spka_combinations()
        spka_volumes, volume_dict = spka_experiment.spka_volumes(
            vol_sub_A=self.vol_sub_A.get(),
            vol_sub_B=self.vol_sub_B.get(),
            vol_cat=self.vol_cat.get(),
            A0=self.A0.get(),
            B0_stand=self.B0_stand.get(),
            B0_DE=self.B0_DE.get(),
            C0_Stand=self.C0_stand.get(),
            C0_DE=self.C0_DE.get()
        )

        # Calculate total number of kinetic profiles
        total_kinetic_profiles = self.num_sub_a * self.num_sub_b * self.num_cat

        # Calculate total number of reaction plugs
        total_reaction_plugs = len([item for sublist in spka_combinations for item in sublist])

        # Open a new window to display the volume information
        volume_window = tk.Toplevel(self.root)
        volume_window.title("Volume Information")

        # Calculate top left corner of the rack
        rack_top_left_x = self.left_padding
        rack_top_left_y = self.rect_padding * 8 + self.circle_diameter

        # Draw the rectangle around the rack
        canvas = tk.Canvas(volume_window, width=self.canvas_width + 200, height=self.canvas_height)
        canvas.pack()
        canvas.create_rectangle(
            rack_top_left_x - self.rect_padding,
            rack_top_left_y - self.rect_padding,
            rack_top_left_x + self.num_cols * (self.circle_diameter + self.inner_padding_x) - self.inner_padding_x + self.rect_padding,
            rack_top_left_y + self.num_rows * (self.circle_diameter + self.inner_padding_y) - self.inner_padding_y + self.rect_padding,
            outline="black"
        )

        # Draw the row numbers aligned with the centers of the circles
        for row in range(self.num_rows):
            canvas.create_text(
                rack_top_left_x - self.rect_padding * 2,
                rack_top_left_y + row * (self.circle_diameter + self.inner_padding_y) + self.circle_diameter / 2,
                text=str(row + 1),
                anchor="e"
            )

        # Draw the column headers rotated by 45 degrees
        variable_names = ['Substrate A', 'Substrate B', 'Catalyst', 'Additive']
        for col in range(self.num_cols):
            canvas.create_text(
                rack_top_left_x + col * (self.circle_diameter + self.inner_padding_x) + self.circle_diameter,
                rack_top_left_y - self.rect_padding * 6,
                text=variable_names[col],
                angle=45,
                anchor="center"
            )

        # Draw the volumes in place of the vials
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x0 = rack_top_left_x + col * (self.circle_diameter + self.inner_padding_x)
                y0 = rack_top_left_y + row * (self.circle_diameter + self.inner_padding_y)
                x1 = x0 + self.circle_diameter
                y1 = y0 + self.circle_diameter
                vial_index = row * self.num_cols + col + 1
                volume = volume_dict.get(vial_index, 0)
                volume_text = "-" if volume == 0 else f"{volume:.2f}"
                canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=volume_text)

        # Display additional information to the right of the rack
        info_x = rack_top_left_x + self.num_cols * (self.circle_diameter + self.inner_padding_x) + self.rect_padding * 2
        info_y = rack_top_left_y

        canvas.create_text(info_x, info_y, text="Total number of kinetic profiles:", anchor="w")
        canvas.create_text(info_x, info_y + 20, text=str(total_kinetic_profiles), anchor="w")

        canvas.create_text(info_x, info_y + 40, text="Total number of reaction plugs:", anchor="w")
        canvas.create_text(info_x, info_y + 60, text=str(total_reaction_plugs), anchor="w")





if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveRack(root)
    root.mainloop()
