import os
import random
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

class BackgroundTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background File Typer")
        self.root.geometry("540x320")
        self.root.resizable(False, False)

        self.input_file = ""
        self.output_file = ""
        self.is_running = False

        # Title
        tk.Label(root, text="Background File Typer (No Mouse/Keyboard Lock)", font=("Helvetica", 12, "bold")).pack(pady=10)

        # Input File Selection
        frame_in = tk.Frame(root)
        frame_in.pack(fill="x", padx=20, pady=5)
        self.entry_in = tk.Entry(frame_in, width=40)
        self.entry_in.pack(side="left", padx=(0, 10))
        tk.Button(frame_in, text="Source File", command=self.browse_input).pack(side="right")

        # Output File Selection (The file you open in VS Code)
        frame_out = tk.Frame(root)
        frame_out.pack(fill="x", padx=20, pady=5)
        self.entry_out = tk.Entry(frame_out, width=40)
        self.entry_out.pack(side="left", padx=(0, 10))
        tk.Button(frame_out, text="Target File", command=self.browse_output).pack(side="right")

        # Status
        self.status_label = tk.Label(root, text="Select files and open the Target File in VS Code.", fg="gray")
        self.status_label.pack(pady=15)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        self.start_btn = tk.Button(btn_frame, text="Start", bg="#4CAF50", fg="white", width=12, command=self.start)
        self.start_btn.pack(side="left", padx=10)
        self.stop_btn = tk.Button(btn_frame, text="Stop", bg="#f44336", fg="white", width=12, state="disabled", command=self.stop)
        self.stop_btn.pack(side="right", padx=10)

    def browse_input(self):
        f = filedialog.askopenfilename(title="Select Code to Read")
        if f:
            self.input_file = f
            self.entry_in.delete(0, tk.END)
            self.entry_in.insert(0, f)

    def browse_output(self):
        f = filedialog.asksaveasfilename(title="Select or Create File to Write To")
        if f:
            self.output_file = f
            self.entry_out.delete(0, tk.END)
            self.entry_out.insert(0, f)

    def start(self):
        self.input_file = self.entry_in.get().strip()
        self.output_file = self.entry_out.get().strip()

        if not os.path.exists(self.input_file) or not self.output_file:
            messagebox.showerror("Error", "Please specify both source and target files!")
            return

        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self.write_loop, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.status_label.config(text="Stopped.", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def write_loop(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Clear target file initially
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write("")

        self.status_label.config(text="Writing to file in background... You can use your PC!", fg="green")

        char_count = 0
        with open(self.output_file, "a", encoding="utf-8", buffering=1) as out:
            for char in content:
                if not self.is_running:
                    break

                out.write(char)
                out.flush() # Forces it to disk immediately so VS Code detects it
                char_count += 1

                # Typing delay
                delay = random.uniform(0.04, 0.16)
                if char in [".", ",", ";", "\n"]:
                    delay += random.uniform(0.3, 0.7)

                # 10-second random human pause
                if char_count > 60 and random.random() < 0.008:
                    pause = random.uniform(9.0, 11.0)
                    time.sleep(pause)
                    char_count = 0

                time.sleep(delay)

        if self.is_running:
            self.status_label.config(text="Finished writing!", fg="green")
            self.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundTyperApp(root)
    root.mainloop()