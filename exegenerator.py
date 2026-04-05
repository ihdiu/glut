"""
Interactive Build Script for Creating Executables with PyInstaller
This script provides a GUI to select Python files and build executables
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading


class ExecutableBuilder:
    """GUI application for building Python executables"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Python to EXE Builder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.python_file = tk.StringVar()
        self.exe_name = tk.StringVar(value="MyApp")
        self.output_dir = tk.StringVar(value="dist")
        self.windowed = tk.BooleanVar(value=True)
        self.onefile = tk.BooleanVar(value=True)
        self.icon_file = tk.StringVar()
        self.is_building = False
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🚀 Python to EXE Builder",
            font=("Arial", 20, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        # File Selection Section
        self.create_file_section(main_frame)
        
        # Configuration Section
        self.create_config_section(main_frame)
        
        # Build Button
        self.create_build_section(main_frame)
        
        # Output Log
        self.create_output_section(main_frame)
        
    def create_file_section(self, parent):
        """Create file selection section"""
        section_frame = ttk.LabelFrame(parent, text="📁 File Selection", padding="15")
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Python file selection
        py_frame = ttk.Frame(section_frame)
        py_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(py_frame, text="Python File:", width=15).pack(side=tk.LEFT)
        ttk.Entry(py_frame, textvariable=self.python_file, state='readonly').pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )
        ttk.Button(
            py_frame,
            text="Browse...",
            command=self.browse_python_file,
            width=12
        ).pack(side=tk.LEFT)
        
        # EXE name
        name_frame = ttk.Frame(section_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="EXE Name:", width=15).pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame, textvariable=self.exe_name)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Add .exe suffix label for Windows
        if sys.platform == "win32":
            ttk.Label(name_frame, text=".exe", foreground="gray").pack(side=tk.LEFT)
        
        # Icon file (optional)
        icon_frame = ttk.Frame(section_frame)
        icon_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(icon_frame, text="Icon (optional):", width=15).pack(side=tk.LEFT)
        ttk.Entry(icon_frame, textvariable=self.icon_file, state='readonly').pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )
        ttk.Button(
            icon_frame,
            text="Browse...",
            command=self.browse_icon_file,
            width=12
        ).pack(side=tk.LEFT)
        
    def create_config_section(self, parent):
        """Create configuration section"""
        section_frame = ttk.LabelFrame(parent, text="⚙️ Build Options", padding="15")
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Options grid
        options_frame = ttk.Frame(section_frame)
        options_frame.pack(fill=tk.X)
        
        # Onefile option
        onefile_check = ttk.Checkbutton(
            options_frame,
            text="📦 Single File (--onefile)",
            variable=self.onefile
        )
        onefile_check.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        # Windowed option
        windowed_check = ttk.Checkbutton(
            options_frame,
            text="🖼️ Windowed (No Console)",
            variable=self.windowed
        )
        windowed_check.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Info labels
        info_frame = ttk.Frame(section_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = "💡 Tip: Use 'Single File' for easy distribution. Use 'Windowed' for GUI apps to hide the console."
        ttk.Label(
            info_frame,
            text=info_text,
            wraplength=700,
            foreground="gray",
            font=("Arial", 9)
        ).pack()
        
    def create_build_section(self, parent):
        """Create build button section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.build_button = tk.Button(
            button_frame,
            text="🔨 Build Executable",
            command=self.start_build,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            cursor="hand2",
            pady=12,
            relief=tk.FLAT
        )
        self.build_button.pack(fill=tk.X)
        
    def create_output_section(self, parent):
        """Create output log section"""
        section_frame = ttk.LabelFrame(parent, text="📋 Build Log", padding="10")
        section_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrolled text widget
        self.output_text = scrolledtext.ScrolledText(
            section_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="white"
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.log_message("Ready to build! Select a Python file and click 'Build Executable'.\n")
        
    def browse_python_file(self):
        """Browse for Python file"""
        filename = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[
                ("Python Files", "*.py"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.python_file.set(filename)
            # Auto-set exe name from filename
            base_name = os.path.splitext(os.path.basename(filename))[0]
            # Convert to PascalCase for exe name
            exe_name = ''.join(word.capitalize() for word in base_name.split('_'))
            self.exe_name.set(exe_name)
            self.log_message(f"✓ Selected: {filename}\n")
            
    def browse_icon_file(self):
        """Browse for icon file"""
        if sys.platform == "win32":
            filetypes = [("Icon Files", "*.ico"), ("All Files", "*.*")]
        elif sys.platform == "darwin":
            filetypes = [("Icon Files", "*.icns"), ("All Files", "*.*")]
        else:
            filetypes = [("Icon Files", "*.ico *.png"), ("All Files", "*.*")]
            
        filename = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=filetypes
        )
        
        if filename:
            self.icon_file.set(filename)
            self.log_message(f"✓ Icon selected: {filename}\n")
            
    def log_message(self, message):
        """Add message to output log"""
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.output_text.update()
        
    def start_build(self):
        """Start the build process in a separate thread"""
        # Validate inputs
        if not self.python_file.get():
            messagebox.showerror("Error", "Please select a Python file!")
            return
            
        if not self.exe_name.get():
            messagebox.showerror("Error", "Please enter an EXE name!")
            return
            
        if self.is_building:
            messagebox.showwarning("Warning", "Build already in progress!")
            return
            
        # Disable button during build
        self.is_building = True
        self.build_button.config(
            state=tk.DISABLED,
            text="⏳ Building...",
            bg="#95a5a6"
        )
        
        # Clear log
        self.output_text.delete(1.0, tk.END)
        
        # Start build in thread
        build_thread = threading.Thread(target=self.build_executable)
        build_thread.daemon = True
        build_thread.start()
        
    def build_executable(self):
        """Build the executable using PyInstaller"""
        try:
            self.log_message("=" * 60 + "\n")
            self.log_message("Starting build process...\n")
            self.log_message("=" * 60 + "\n\n")
            
            # Check if PyInstaller is installed
            self.log_message("Checking for PyInstaller...\n")
            try:
                import PyInstaller
                self.log_message("✓ PyInstaller is installed\n\n")
            except ImportError:
                self.log_message("✗ PyInstaller not found. Installing...\n")
                try:
                    self.install_pyinstaller()
                    self.log_message("✓ PyInstaller installed successfully\n\n")
                except Exception as e:
                    self.log_message(f"✗ Failed to install PyInstaller: {e}\n")
                    raise Exception(f"PyInstaller installation failed: {e}")
            
            # Verify PyInstaller can be run
            self.log_message("Verifying PyInstaller installation...\n")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "PyInstaller", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.log_message(f"✓ PyInstaller version: {result.stdout.strip()}\n\n")
                else:
                    raise Exception("PyInstaller verification failed")
            except Exception as e:
                self.log_message(f"✗ PyInstaller verification failed: {e}\n")
                self.log_message("\nTrying to reinstall PyInstaller...\n")
                self.install_pyinstaller()
                self.log_message("✓ PyInstaller reinstalled\n\n")
            
            # Build command - use python -m PyInstaller for better compatibility
            cmd = [sys.executable, "-m", "PyInstaller"]
            
            # Add options
            if self.onefile.get():
                cmd.append("--onefile")
                self.log_message("✓ Option: Single file executable\n")
                
            if self.windowed.get():
                cmd.append("--windowed")
                self.log_message("✓ Option: Windowed (no console)\n")
                
            if self.icon_file.get():
                cmd.extend(["--icon", self.icon_file.get()])
                self.log_message(f"✓ Option: Icon file - {self.icon_file.get()}\n")
                
            cmd.extend(["--name", self.exe_name.get()])
            cmd.append("--clean")
            cmd.append(self.python_file.get())
            
            self.log_message(f"\n{'=' * 60}\n")
            self.log_message(f"Build command:\n{' '.join(cmd)}\n")
            self.log_message(f"{'=' * 60}\n\n")
            
            # Run PyInstaller
            self.log_message("Building executable (this may take a few minutes)...\n\n")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output
            for line in process.stdout:
                self.log_message(line)
                
            process.wait()
            
            if process.returncode == 0:
                self.log_message(f"\n{'=' * 60}\n")
                self.log_message("✅ BUILD SUCCESSFUL!\n")
                self.log_message(f"{'=' * 60}\n\n")
                
                exe_name = self.exe_name.get()
                if sys.platform == "win32":
                    exe_name += ".exe"
                    
                exe_path = os.path.join("dist", exe_name)
                self.log_message(f"📦 Your executable is ready:\n")
                self.log_message(f"   {os.path.abspath(exe_path)}\n\n")
                
                if os.path.exists(exe_path):
                    size = os.path.getsize(exe_path) / (1024 * 1024)
                    self.log_message(f"📊 File size: {size:.2f} MB\n\n")
                
                self.log_message("You can now distribute this file to users!\n")
                self.log_message("No Python installation required on their computers.\n\n")
                
                # Show success dialog
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Executable built successfully!\n\nLocation: {os.path.abspath(exe_path)}"
                ))
                
                # Ask to open folder
                self.root.after(0, lambda: self.ask_open_folder())
                
            else:
                self.log_message(f"\n{'=' * 60}\n")
                self.log_message("❌ BUILD FAILED!\n")
                self.log_message(f"{'=' * 60}\n")
                self.log_message("Check the log above for error details.\n")
                
                self.root.after(0, lambda: messagebox.showerror(
                    "Build Failed",
                    "The build process failed. Check the log for details."
                ))
                
        except Exception as e:
            self.log_message(f"\n❌ Error: {str(e)}\n")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            
        finally:
            # Re-enable button
            self.is_building = False
            self.root.after(0, self.reset_build_button)
            
    def install_pyinstaller(self):
        """Install PyInstaller"""
        self.log_message("Installing PyInstaller...\n")
        self.log_message("-" * 60 + "\n")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                self.log_message(line)
                
            process.wait()
            
            if process.returncode != 0:
                raise Exception("pip install failed")
                
            self.log_message("-" * 60 + "\n")
            self.log_message("✓ PyInstaller installation complete\n")
            
        except Exception as e:
            self.log_message(f"\n✗ Installation error: {e}\n")
            raise Exception(f"Failed to install PyInstaller: {e}\n\nTry running manually:\n  pip install pyinstaller")
            
    def reset_build_button(self):
        """Reset build button state"""
        self.build_button.config(
            state=tk.NORMAL,
            text="🔨 Build Executable",
            bg="#27ae60"
        )
        
    def ask_open_folder(self):
        """Ask user if they want to open the output folder"""
        result = messagebox.askyesno(
            "Open Folder",
            "Do you want to open the output folder?"
        )
        
        if result:
            dist_path = os.path.abspath("dist")
            if sys.platform == "win32":
                os.startfile(dist_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", dist_path])
            else:
                subprocess.Popen(["xdg-open", dist_path])


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ExecutableBuilder(root)
    root.mainloop()


if __name__ == "__main__":
    main()