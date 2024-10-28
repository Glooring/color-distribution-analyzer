import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image
import numpy as np
from tkinterdnd2 import TkinterDnD, DND_FILES  # Drag-and-drop support
from threading import Thread
from collections import Counter

# Placeholder for background imports
plt = None

# Thread function to load heavy libraries in the background
def background_imports():
    global plt
    import matplotlib
    matplotlib.use("TkAgg")  # or "Qt5Agg" if you prefer Qt
    import matplotlib.pyplot as plt

# Start the background import thread
Thread(target=background_imports, daemon=True).start()

class ColorDistributionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Distribution Analyzer")
        
        # Set the initial window size and center it
        window_width, window_height = 600, 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_left = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")
        
        # Make the window resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        self.image_path = tk.StringVar()
        self.sensitivity_enabled = tk.BooleanVar(value=False)
        self.sensitivity_value = tk.DoubleVar(value=30.0)
        
        self.placeholder_text = '// example:\n#FFDF7F, #FF9F7F, #FFBF00'
        self.text_modified = False  # Track if user has modified the placeholder

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 10))
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure main_frame to be resizable
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=0)
        
        # Image selection
        image_frame = ttk.LabelFrame(main_frame, text="Image Selection", padding="10")
        image_frame.grid(row=0, column=0, sticky='ew', pady=5)
        image_frame.columnconfigure(1, weight=1)  # Make the entry field expandable
        
        image_label = ttk.Label(image_frame, text="Image File:")
        image_label.grid(row=0, column=0, sticky='w')
        
        image_entry = ttk.Entry(image_frame, textvariable=self.image_path, width=40)
        image_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        # Change the button text to "Choose File"
        choose_file_button = ttk.Button(image_frame, text="Select or Drop File", command=self.choose_file)
        choose_file_button.grid(row=0, column=2)
        
        # Enable drag-and-drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_image_file)

        # Sensitivity option
        sensitivity_frame = ttk.LabelFrame(main_frame, text="Sensitivity Option", padding="10")
        sensitivity_frame.grid(row=1, column=0, sticky='ew', pady=5)
        sensitivity_frame.columnconfigure(1, weight=1)
        
        sensitivity_check = ttk.Checkbutton(sensitivity_frame, text="Enable Sensitivity", variable=self.sensitivity_enabled, command=self.toggle_sensitivity)
        sensitivity_check.grid(row=0, column=0, sticky='w')
        
        self.sensitivity_entry = ttk.Entry(sensitivity_frame, textvariable=self.sensitivity_value, width=10, state='disabled')
        self.sensitivity_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        # Text entry for comma-separated colors with placeholder
        color_frame = ttk.LabelFrame(main_frame, text="Colors to Search", padding="10")
        color_frame.grid(row=2, column=0, sticky='nsew', pady=5)
        color_frame.columnconfigure(0, weight=1)
        color_frame.rowconfigure(0, weight=1)
        
        self.color_text = tk.Text(color_frame, height=4, wrap='word', fg='gray')
        self.color_text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.color_text.insert(tk.END, self.placeholder_text)

        # Bind focus events to manage placeholder behavior
        self.color_text.bind("<FocusIn>", self.clear_placeholder)
        self.color_text.bind("<FocusOut>", self.add_placeholder)

        # Generate button
        generate_button = ttk.Button(main_frame, text="Generate Pie Chart", command=self.on_generate_click)
        generate_button.grid(row=3, column=0, pady=10, sticky='ew')
        
    def clear_placeholder(self, event=None):
        """Clear the placeholder text on focus in, if it hasn't been modified."""
        if not self.text_modified:
            self.color_text.delete("1.0", tk.END)
            self.color_text.config(fg='black')
            self.text_modified = True
    
    def add_placeholder(self, event=None):
        """Re-add the placeholder text if the text box is empty on focus out."""
        if not self.color_text.get("1.0", tk.END).strip():
            self.color_text.insert("1.0", self.placeholder_text)
            self.color_text.config(fg='gray')
            self.text_modified = False

    def choose_file(self):
        """Open file dialog to choose an image file."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image_path.set(file_path)

    def drop_image_file(self, event):
        """Handle file drop event to set image path from drag-and-drop."""
        file_path = event.data.strip('{}')  # Remove curly braces for paths with spaces
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            self.image_path.set(file_path)
        else:
            messagebox.showerror("Invalid File", "Please drop a valid image file.")

    def toggle_sensitivity(self):
        if self.sensitivity_enabled.get():
            self.sensitivity_entry.config(state='normal')
        else:
            self.sensitivity_entry.config(state='disabled')
        
    def get_colors_from_text(self):
        """Extracts colors from the text box input as a list of hex codes."""
        color_text = self.color_text.get("1.0", tk.END).strip()
        if color_text == self.placeholder_text:
            return []  # Return an empty list if only the placeholder text is present
        colors = [color.strip().strip('"') for color in color_text.split(",") if color.strip()]
        return colors
    
    def on_generate_click(self):
        """Start generating the pie chart in a new thread to keep the UI responsive."""
        Thread(target=self.generate_pie_chart).start()

    def generate_pie_chart(self):
        image_path = self.image_path.get()
        if not image_path:
            messagebox.showerror("No Image", "Please select an image file.")
            return
        colors = self.get_colors_from_text()
        if not colors:
            messagebox.showerror("No Colors", "Please add colors in the text box to search in the image.")
            return
        try:
            sensitivity = self.sensitivity_value.get() if self.sensitivity_enabled.get() else 0
            pixels = self.load_image(image_path)
            color_counts = self.match_colors(pixels, colors, sensitivity)
            if color_counts:
                self.plot_color_distribution(color_counts)
            else:
                messagebox.showinfo("No Colors Found", f"No matching colors were found in the image within a sensitivity threshold of {sensitivity}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
    def load_image(self, image_path):
        image = Image.open(image_path).convert('RGB')
        pixels = np.array(image)
        return pixels.reshape(-1, 3)
    
    def color_distance(self, c1, c2):
        return np.sqrt(np.sum((np.array(c1) - np.array(c2)) ** 2))
    
    def match_colors(self, pixels, color_list, sensitivity):
        color_rgb_list = [tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) for color in color_list]
        color_counter = Counter(map(tuple, pixels))
        matched_color_counts = {color: 0 for color in color_rgb_list}
        
        for pixel, count in color_counter.items():
            for ref_color in color_rgb_list:
                if sensitivity == 0:
                    if pixel == ref_color:
                        matched_color_counts[ref_color] += count
                        break
                else:
                    if self.color_distance(pixel, ref_color) <= sensitivity:
                        matched_color_counts[ref_color] += count
                        break
        matched_color_counts = {color: count for color, count in matched_color_counts.items() if count > 0}
        return matched_color_counts
    
    def plot_color_distribution(self, color_counts):
        global plt  # Use the matplotlib module loaded in the background
        total_pixels = sum(color_counts.values())
        colors = [f"#{''.join(f'{value:02X}' for value in color)}" for color in color_counts.keys()]
        values = list(color_counts.values())
        percentages = [(count / total_pixels) * 100 for count in values]
        
        labels = [f"{colors[i]} ({percentages[i]:.1f}%)" for i in range(len(colors))]
        
        # Plot the pie chart with adjusted chart positioning
        fig, ax = plt.subplots(figsize=(6, 4.7))
        wedges, texts = ax.pie(
            values, labels=None, colors=colors, startangle=90
        )

        # Move the pie chart slightly to the right
        ax.set_position([0.36, 0.1, 0.6, 0.8])  # [left, bottom, width, height]

        # Set up the legend on the left side
        handles = [plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=col, markersize=15) for col in colors]
        ax.legend(handles, labels, loc='center left', bbox_to_anchor=(-0.54, 0.5), title="Legend")

        # Center the title over the entire figure
        fig.suptitle("Color Distribution in Image", x=0.5, y=0.95, ha='center', fontsize=14)
        
        # Center the matplotlib window on the screen
        fig.canvas.manager.window.wm_geometry(f"600x470+{self.root.winfo_screenwidth()//2 - 300}+{self.root.winfo_screenheight()//2 - 225}")
        
        plt.show()
    
if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Enable drag-and-drop functionality
    app = ColorDistributionApp(root)
    root.mainloop()
