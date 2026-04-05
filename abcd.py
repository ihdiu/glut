#!/usr/bin/env python3
"""
GLUT Shape Code Generator - Desktop Application
A tkinter-based tool to draw shapes and generate OpenGL/GLUT code
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import math
from typing import List, Tuple, Optional, Dict


class Point:
    """Represents a 2D point on the canvas"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class GLUTCodeGenerator:
    """Main application class for GLUT Code Generator"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GLUT Shape Code Generator")
        self.root.geometry("1800x900")  # Increased height for better visibility
        
        # Configure colors matching the web version
        self.colors = {
            'primary': '#667eea',
            'primary_dark': '#764ba2',
            'success': '#48bb78',
            'danger': '#f56565',
            'bg_light': '#f7fafc',
            'border': '#e2e8f0',
            'text_dark': '#1a202c',
            'text_medium': '#4a5568',
            'text_light': '#718096'
        }
        
        # Application state
        self.points: List[Point] = []
        self.current_mode = 'polygon'
        self.circle_center: Optional[Point] = None
        self.circle_radius_point: Optional[Point] = None
        self.image = None
        self.photo_image = None
        self.shape_color = '#667eea'
        
        # Canvas dimensions
        self.canvas_width = 400
        self.canvas_height = 400
        
        # Setup UI
        self.setup_ui()
        self.update_point_count()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Configure root
        self.root.configure(bg='#667eea')
        
        # Main container with gradient-like background
        main_container = tk.Frame(self.root, bg='#667eea')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create sidebar and main content area
        self.create_sidebar(main_container)
        self.create_main_content(main_container)
        
    def create_sidebar(self, parent):
        """Create the sidebar with controls"""
        sidebar = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.config(width=320)
        
        # Prevent sidebar from shrinking
        sidebar.pack_propagate(False)
        
        # Scrollable frame for sidebar content
        canvas = tk.Canvas(sidebar, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(sidebar, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=300)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas width changes to update window width
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width - 20)
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        # Bind mouse wheel for different platforms
        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows/Mac
        canvas.bind_all("<Button-4>", on_mousewheel_linux)  # Linux
        canvas.bind_all("<Button-5>", on_mousewheel_linux)  # Linux
        
        # Title
        title_frame = tk.Frame(scrollable_frame, bg='white')
        title_frame.pack(fill=tk.X, padx=24, pady=(24, 8))
        
        title_label = tk.Label(
            title_frame,
            text="🎲 GLUT Generator",
            font=("Arial", 18, "bold"),
            bg='white',
            fg=self.colors['text_dark']
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_frame,
            text="Draw shapes and generate OpenGL code",
            font=("Arial", 10),
            bg='white',
            fg=self.colors['text_light']
        )
        subtitle_label.pack(anchor='w')
        
        # Image section
        self.create_section(scrollable_frame, "IMAGE", self.create_image_controls)
        
        # Axis configuration section
        self.create_section(scrollable_frame, "AXIS CONFIGURATION", self.create_axis_controls)
        
        # Primitive type section
        self.create_section(scrollable_frame, "PRIMITIVE TYPE", self.create_mode_controls)
        
        # Color section
        self.create_section(scrollable_frame, "COLOR", self.create_color_controls)
        
        # Actions section
        self.create_section(scrollable_frame, "ACTIONS", self.create_action_controls)
        
        # Status section (with extra bottom padding)
        self.create_status_section(scrollable_frame)
        
        # Add extra space at bottom to ensure everything is scrollable
        extra_space = tk.Frame(scrollable_frame, bg='white', height=50)
        extra_space.pack(fill=tk.X)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store canvas reference for cleanup
        self.sidebar_canvas = canvas
        
    def create_section(self, parent, title: str, content_creator):
        """Create a section with title and content"""
        section_frame = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.FLAT, bd=1)
        section_frame.pack(fill=tk.X, padx=24, pady=12)
        
        # Section title
        title_frame = tk.Frame(section_frame, bg=self.colors['bg_light'])
        title_frame.pack(fill=tk.X, padx=16, pady=(12, 8))
        
        # Title with accent bar
        accent = tk.Frame(title_frame, bg=self.colors['primary'], width=3, height=14)
        accent.pack(side=tk.LEFT, padx=(0, 8))
        
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Arial", 9, "bold"),
            bg=self.colors['bg_light'],
            fg=self.colors['text_medium']
        )
        title_label.pack(side=tk.LEFT)
        
        # Content
        content_frame = tk.Frame(section_frame, bg=self.colors['bg_light'])
        content_frame.pack(fill=tk.X, padx=16, pady=(0, 12))
        content_creator(content_frame)
        
    def create_image_controls(self, parent):
        """Create image upload controls"""
        btn = tk.Button(
            parent,
            text="📁 Load Image",
            command=self.load_image,
            bg=self.colors['primary'],
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        btn.pack(fill=tk.X)
        
    def create_axis_controls(self, parent):
        """Create axis configuration controls"""
        grid_frame = tk.Frame(parent, bg=self.colors['bg_light'])
        grid_frame.pack(fill=tk.X)
        
        # Create grid layout
        labels = [("X Min:", 0, 0), ("X Max:", 0, 1), ("Y Min:", 1, 0), ("Y Max:", 1, 1)]
        defaults = ["-1.0", "1.0", "-1.0", "1.0"]
        self.axis_vars = {}
        
        for i, ((label_text, row, col), default) in enumerate(zip(labels, defaults)):
            # Label
            label = tk.Label(
                grid_frame,
                text=label_text,
                font=("Arial", 9, "bold"),
                bg=self.colors['bg_light'],
                fg=self.colors['text_medium']
            )
            label.grid(row=row*2, column=col, sticky='w', padx=6, pady=(0, 4))
            
            # Entry
            var = tk.StringVar(value=default)
            entry = tk.Entry(
                grid_frame,
                textvariable=var,
                font=("Arial", 10),
                relief=tk.FLAT,
                bg='white',
                fg=self.colors['text_dark'],
                highlightthickness=2,
                highlightbackground=self.colors['border'],
                highlightcolor=self.colors['primary']
            )
            entry.grid(row=row*2+1, column=col, sticky='ew', padx=6, pady=(0, 12))
            
            # Store variable
            key = label_text.replace(":", "").replace(" ", "_").lower()
            self.axis_vars[key] = var
        
        # Configure grid weights
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        
    def create_mode_controls(self, parent):
        """Create primitive type mode buttons"""
        modes = [
            ("Polygon", "polygon"),
            ("Quads", "quads"),
            ("Lines", "lines"),
            ("Line Loop", "line_loop"),
            ("Circle", "circle"),
            ("Triangles", "triangles")
        ]
        
        # Create grid
        for i, (text, mode) in enumerate(modes):
            row = i // 2
            col = i % 2
            
            btn = tk.Button(
                parent,
                text=text,
                command=lambda m=mode: self.set_mode(m),
                font=("Arial", 9, "bold"),
                relief=tk.FLAT,
                cursor='hand2',
                padx=10,
                pady=8
            )
            btn.grid(row=row, column=col, sticky='ew', padx=4, pady=4)
            
            # Store button reference
            if not hasattr(self, 'mode_buttons'):
                self.mode_buttons = {}
            self.mode_buttons[mode] = btn
            
            # Set initial state
            if mode == 'polygon':
                btn.config(bg=self.colors['primary'], fg='white')
            else:
                btn.config(bg='white', fg=self.colors['text_medium'])
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        
    def create_color_controls(self, parent):
        """Create color picker controls"""
        label = tk.Label(
            parent,
            text="Shape Color:",
            font=("Arial", 9, "bold"),
            bg=self.colors['bg_light'],
            fg=self.colors['text_medium']
        )
        label.pack(anchor='w', pady=(0, 6))
        
        # Color picker button
        self.color_btn = tk.Button(
            parent,
            text="  ",
            bg=self.shape_color,
            command=self.choose_color,
            relief=tk.FLAT,
            cursor='hand2',
            width=40,
            height=2
        )
        self.color_btn.pack(fill=tk.X)
        
    def create_action_controls(self, parent):
        """Create action buttons"""
        # Generate Code button
        gen_btn = tk.Button(
            parent,
            text="💻 Generate Code",
            command=self.generate_code,
            bg=self.colors['success'],
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        gen_btn.pack(fill=tk.X, pady=(0, 8))
        
        # Clear Points button
        clear_btn = tk.Button(
            parent,
            text="🗑️ Clear Points",
            command=self.clear_points,
            bg=self.colors['danger'],
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        clear_btn.pack(fill=tk.X)
        
    def create_status_section(self, parent):
        """Create status section at bottom of sidebar"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.FLAT, bd=1)
        status_frame.pack(fill=tk.X, padx=24, pady=24)
        
        content = tk.Frame(status_frame, bg=self.colors['bg_light'])
        content.pack(fill=tk.X, padx=16, pady=12)
        
        # Status badge
        badge = tk.Label(
            content,
            text="● Ready",
            font=("Arial", 9, "bold"),
            bg='#c6f6d5',
            fg='#22543d',
            padx=10,
            pady=4
        )
        badge.pack(side=tk.LEFT)
        
        # Point count
        self.point_count_label = tk.Label(
            content,
            text="0 points",
            font=("Arial", 9),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light']
        )
        self.point_count_label.pack(side=tk.RIGHT)
        
    def create_main_content(self, parent):
        """Create main content area with canvas and output"""
        main_frame = tk.Frame(parent, bg='#667eea')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Use pack with proper weights for vertical distribution
        # Canvas section - takes most space
        self.create_canvas_section(main_frame)
        
        # Output section - fixed height at bottom
        self.create_output_section(main_frame)
        
    def create_canvas_section(self, parent):
        """Create canvas section"""
        canvas_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Set minimum height
        canvas_frame.config(height=400)
        
        # Header
        header = tk.Frame(canvas_frame, bg='white')
        header.pack(fill=tk.X, padx=24, pady=(24, 16))
        
        title = tk.Label(
            header,
            text="Drawing Canvas",
            font=("Arial", 14, "bold"),
            bg='white',
            fg=self.colors['text_dark']
        )
        title.pack(side=tk.LEFT)
        
        info = tk.Label(
            header,
            text="Click to place points",
            font=("Arial", 9),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            padx=12,
            pady=6
        )
        info.pack(side=tk.RIGHT)
        
        # Canvas wrapper
        canvas_wrapper = tk.Frame(canvas_frame, bg=self.colors['bg_light'])
        canvas_wrapper.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        # Canvas
        self.canvas = tk.Canvas(
            canvas_wrapper,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            highlightthickness=2,
            highlightbackground=self.colors['border'],
            cursor='crosshair'
        )
        self.canvas.pack(expand=True)
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-z>', self.undo_point)
        self.root.bind('<Command-z>', self.undo_point)  # For macOS
        
        # Draw initial state
        self.draw_initial_state()
        
    def create_output_section(self, parent):
        """Create code output section"""
        output_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        output_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 0))
        output_frame.config(height=280)
        output_frame.pack_propagate(False)
        
        # Header
        header = tk.Frame(output_frame, bg='white')
        header.pack(fill=tk.X, padx=24, pady=(24, 12))
        
        title = tk.Label(
            header,
            text="Generated Code",
            font=("Arial", 14, "bold"),
            bg='white',
            fg=self.colors['text_dark']
        )
        title.pack(side=tk.LEFT)
        
        copy_btn = tk.Button(
            header,
            text="📋 Copy",
            command=self.copy_code,
            bg=self.colors['bg_light'],
            fg=self.colors['text_medium'],
            font=("Arial", 9, "bold"),
            relief=tk.FLAT,
            cursor='hand2',
            padx=12,
            pady=6
        )
        copy_btn.pack(side=tk.RIGHT)
        
        # Text widget for code output
        text_frame = tk.Frame(output_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Text widget
        self.code_output = tk.Text(
            text_frame,
            font=("Courier New", 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text_dark'],
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary'],
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            wrap=tk.NONE
        )
        self.code_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code_output.insert('1.0', 'Your generated GLUT code will appear here...')
        self.code_output.config(state=tk.DISABLED)
        
        y_scrollbar.config(command=self.code_output.yview)
        x_scrollbar.config(command=self.code_output.xview)
        
    def draw_initial_state(self):
        """Draw initial canvas state"""
        self.canvas.delete('all')
        self.draw_grid()
        
    def draw_grid(self):
        """Draw grid on canvas"""
        grid_size = 10
        
        # Draw vertical lines
        for x in range(grid_size, self.canvas_width, grid_size):
            self.canvas.create_line(
                x, 0, x, self.canvas_height,
                fill='#cbd5e0',
                width=1
            )
        
        # Draw horizontal lines
        for y in range(grid_size, self.canvas_height, grid_size):
            self.canvas.create_line(
                0, y, self.canvas_width, y,
                fill='#cbd5e0',
                width=1
            )
        
    def redraw_canvas(self):
        """Redraw all canvas content"""
        self.canvas.delete('all')
        
        # Draw image if loaded
        if self.image and self.photo_image:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        
        # Draw grid
        self.draw_grid()
        
        # Draw points and shapes
        self.draw_points_and_shapes()
        
        # Update point count
        self.update_point_count()
        
    def draw_points_and_shapes(self):
        """Draw points and connecting lines based on current mode"""
        # Draw regular points
        for i, point in enumerate(self.points):
            # Draw point
            self.canvas.create_oval(
                point.x - 4, point.y - 4,
                point.x + 4, point.y + 4,
                fill=self.colors['primary'],
                outline='white',
                width=2
            )
            
            # Draw connecting lines based on mode
            if self.current_mode == 'polygon' or self.current_mode == 'line_loop':
                if i > 0:
                    self.canvas.create_line(
                        self.points[i-1].x, self.points[i-1].y,
                        point.x, point.y,
                        fill=self.colors['primary'],
                        width=2
                    )
            elif self.current_mode == 'lines':
                if i > 0 and i % 2 == 1:
                    self.canvas.create_line(
                        self.points[i-1].x, self.points[i-1].y,
                        point.x, point.y,
                        fill=self.colors['primary'],
                        width=2
                    )
            elif self.current_mode == 'quads':
                if (i + 1) % 4 == 0 and i >= 3:
                    points_list = [
                        self.points[i-3].x, self.points[i-3].y,
                        self.points[i-2].x, self.points[i-2].y,
                        self.points[i-1].x, self.points[i-1].y,
                        self.points[i].x, self.points[i].y
                    ]
                    self.canvas.create_polygon(
                        points_list,
                        outline=self.colors['primary'],
                        fill='',
                        width=2
                    )
            elif self.current_mode == 'triangles':
                if (i + 1) % 3 == 0 and i >= 2:
                    points_list = [
                        self.points[i-2].x, self.points[i-2].y,
                        self.points[i-1].x, self.points[i-1].y,
                        self.points[i].x, self.points[i].y
                    ]
                    self.canvas.create_polygon(
                        points_list,
                        outline=self.colors['primary'],
                        fill='',
                        width=2
                    )
        
        # Draw circle
        if self.current_mode == 'circle':
            if self.circle_center:
                # Draw center point
                self.canvas.create_oval(
                    self.circle_center.x - 5, self.circle_center.y - 5,
                    self.circle_center.x + 5, self.circle_center.y + 5,
                    fill=self.colors['success'],
                    outline='white',
                    width=2
                )
                self.canvas.create_text(
                    self.circle_center.x + 10, self.circle_center.y - 10,
                    text='Center',
                    font=("Arial", 10, "bold"),
                    anchor='w'
                )
                
            if self.circle_radius_point:
                # Draw radius point
                self.canvas.create_oval(
                    self.circle_radius_point.x - 5, self.circle_radius_point.y - 5,
                    self.circle_radius_point.x + 5, self.circle_radius_point.y + 5,
                    fill=self.colors['danger'],
                    outline='white',
                    width=2
                )
                
                # Draw circle
                if self.circle_center:
                    radius = self.calculate_distance(
                        self.circle_center,
                        self.circle_radius_point
                    )
                    self.canvas.create_oval(
                        self.circle_center.x - radius, self.circle_center.y - radius,
                        self.circle_center.x + radius, self.circle_center.y + radius,
                        outline=self.colors['primary'],
                        width=3
                    )
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        x, y = event.x, event.y
        
        if self.current_mode == 'circle':
            if not self.circle_center:
                self.circle_center = Point(x, y)
            elif not self.circle_radius_point:
                self.circle_radius_point = Point(x, y)
            else:
                # Reset for new circle
                self.circle_center = Point(x, y)
                self.circle_radius_point = None
        else:
            self.points.append(Point(x, y))
        
        self.redraw_canvas()
        
    def on_canvas_motion(self, event):
        """Handle canvas motion for circle preview"""
        if self.current_mode == 'circle' and self.circle_center and not self.circle_radius_point:
            # Redraw canvas
            self.redraw_canvas()
            
            # Draw preview circle
            radius = self.calculate_distance(
                self.circle_center,
                Point(event.x, event.y)
            )
            self.canvas.create_oval(
                self.circle_center.x - radius, self.circle_center.y - radius,
                self.circle_center.x + radius, self.circle_center.y + radius,
                outline=self.colors['primary'],
                width=2,
                dash=(5, 5)
            )
    
    def calculate_distance(self, p1: Point, p2: Point) -> float:
        """Calculate distance between two points"""
        return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
    
    def undo_point(self, event=None):
        """Undo last point (Ctrl+Z)"""
        if self.current_mode == 'circle':
            if self.circle_radius_point:
                self.circle_radius_point = None
            elif self.circle_center:
                self.circle_center = None
        else:
            if self.points:
                self.points.pop()
        
        self.redraw_canvas()
        
    def set_mode(self, mode: str):
        """Set drawing mode"""
        self.current_mode = mode
        
        if mode != 'circle':
            self.circle_center = None
            self.circle_radius_point = None
        
        # Update button states
        for btn_mode, btn in self.mode_buttons.items():
            if btn_mode == mode:
                btn.config(bg=self.colors['primary'], fg='white')
            else:
                btn.config(bg='white', fg=self.colors['text_medium'])
        
        self.redraw_canvas()
        
    def load_image(self):
        """Load an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Load and resize image
                img = Image.open(file_path)
                img = img.resize((self.canvas_width, self.canvas_height), Image.LANCZOS)
                self.image = img
                self.photo_image = ImageTk.PhotoImage(img)
                self.redraw_canvas()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def choose_color(self):
        """Open color chooser dialog"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(initialcolor=self.shape_color)
        if color[1]:
            self.shape_color = color[1]
            self.color_btn.config(bg=self.shape_color)
    
    def hex_to_gl_color(self, hex_color: str) -> Dict[str, float]:
        """Convert hex color to GL RGB values"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return {'r': round(r, 2), 'g': round(g, 2), 'b': round(b, 2)}
    
    def convert_coords(self, x: float, y: float) -> Tuple[float, float]:
        """Convert canvas coordinates to OpenGL coordinates"""
        try:
            x_min = float(self.axis_vars['x_min'].get())
            x_max = float(self.axis_vars['x_max'].get())
            y_min = float(self.axis_vars['y_min'].get())
            y_max = float(self.axis_vars['y_max'].get())
            
            gl_x = x_min + (x / self.canvas_width) * (x_max - x_min)
            gl_y = y_max - (y / self.canvas_height) * (y_max - y_min)
            
            return (gl_x, gl_y)
        except ValueError:
            return (0.0, 0.0)
    
    def generate_code(self):
        """Generate GLUT code based on current points and mode"""
        try:
            x_min = float(self.axis_vars['x_min'].get())
            x_max = float(self.axis_vars['x_max'].get())
            y_min = float(self.axis_vars['y_min'].get())
            y_max = float(self.axis_vars['y_max'].get())
            
            if x_min >= x_max or y_min >= y_max:
                self.set_code_output('// Invalid axis range. Min must be less than max.')
                return
                
        except ValueError:
            self.set_code_output('// Invalid axis values. Please enter numbers.')
            return
        
        color = self.hex_to_gl_color(self.shape_color)
        color_line = f"glColor3f({color['r']}f, {color['g']}f, {color['b']}f);\n"
        
        code = ""
        
        if self.current_mode == 'circle':
            if not self.circle_center or not self.circle_radius_point:
                self.set_code_output('// Please select center and radius point for circle')
                return
            
            radius_screen = self.calculate_distance(self.circle_center, self.circle_radius_point)
            center = self.convert_coords(self.circle_center.x, self.circle_center.y)
            radius_gl = (radius_screen / self.canvas_width) * (x_max - x_min)
            
            code = f"""float cx = {center[0]:.2f}f, cy = {center[1]:.2f}f;  // center
float r = {radius_gl:.2f}f;  // radius
int i;

{color_line}glBegin(GL_POLYGON);
for (i = 0; i < 100; i++)
{{
    float angle = 2 * 3.1416f * i / 100;
    glVertex2f(cx + r * cos(angle),
               cy + r * sin(angle));
}}
glEnd();"""
        
        elif self.current_mode == 'polygon':
            if len(self.points) < 3:
                self.set_code_output('// Need at least 3 points for polygon')
                return
            
            code = f"{color_line}glBegin(GL_POLYGON);\n"
            for point in self.points:
                coords = self.convert_coords(point.x, point.y)
                code += f"    glVertex2f({coords[0]:.2f}f, {coords[1]:.2f}f);\n"
            code += "glEnd();"
        
        elif self.current_mode == 'triangles':
            if len(self.points) < 3:
                self.set_code_output('// Need at least 3 points for triangles')
                return
            
            if len(self.points) % 3 != 0:
                self.set_code_output(f'// Need multiple of 3 points for triangles. Currently have {len(self.points)} points.')
                return
            
            code = f"{color_line}glBegin(GL_TRIANGLES);\n"
            for i in range(0, len(self.points), 3):
                for j in range(3):
                    coords = self.convert_coords(self.points[i + j].x, self.points[i + j].y)
                    code += f"    glVertex2f({coords[0]:.2f}f, {coords[1]:.2f}f);\n"
            code += "glEnd();"
        
        elif self.current_mode == 'quads':
            if len(self.points) < 4:
                self.set_code_output('// Need at least 4 points for quads (points must be multiple of 4)')
                return
            
            if len(self.points) % 4 != 0:
                self.set_code_output(f'// Need multiple of 4 points for quads. Currently have {len(self.points)} points.')
                return
            
            code = f"{color_line}glBegin(GL_QUADS);\n"
            for i in range(0, len(self.points), 4):
                for j in range(4):
                    coords = self.convert_coords(self.points[i + j].x, self.points[i + j].y)
                    code += f"    glVertex2f({coords[0]:.2f}f, {coords[1]:.2f}f);\n"
            code += "glEnd();"
        
        elif self.current_mode == 'lines':
            if len(self.points) < 2:
                self.set_code_output('// Need at least 2 points for lines')
                return
            
            if len(self.points) % 2 != 0:
                self.set_code_output(f'// Need even number of points for lines. Currently have {len(self.points)} points.')
                return
            
            code = f"{color_line}glBegin(GL_LINES);\n"
            for i in range(0, len(self.points), 2):
                for j in range(2):
                    coords = self.convert_coords(self.points[i + j].x, self.points[i + j].y)
                    code += f"    glVertex2f({coords[0]:.2f}f, {coords[1]:.2f}f);\n"
            code += "glEnd();"
        
        elif self.current_mode == 'line_loop':
            if len(self.points) < 2:
                self.set_code_output('// Need at least 2 points for line loop')
                return
            
            code = f"{color_line}glBegin(GL_LINE_LOOP);\n"
            for point in self.points:
                coords = self.convert_coords(point.x, point.y)
                code += f"    glVertex2f({coords[0]:.2f}f, {coords[1]:.2f}f);\n"
            code += "glEnd();"
        
        self.set_code_output(code)
    
    def set_code_output(self, code: str):
        """Set the code output text"""
        self.code_output.config(state=tk.NORMAL)
        self.code_output.delete('1.0', tk.END)
        self.code_output.insert('1.0', code)
        self.code_output.config(state=tk.DISABLED)
    
    def copy_code(self):
        """Copy generated code to clipboard"""
        code = self.code_output.get('1.0', tk.END).strip()
        if code and code != 'Your generated GLUT code will appear here...':
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Success", "Code copied to clipboard!")
    
    def clear_points(self):
        """Clear all points and reset"""
        self.points.clear()
        self.circle_center = None
        self.circle_radius_point = None
        self.redraw_canvas()
        self.set_code_output('Your generated GLUT code will appear here...')
    
    def update_point_count(self):
        """Update the point count label"""
        if self.current_mode == 'circle':
            count = 0
            if self.circle_center:
                count = 1
            if self.circle_radius_point:
                count = 2
        else:
            count = len(self.points)
        
        plural = '' if count == 1 else 's'
        self.point_count_label.config(text=f"{count} point{plural}")
    
    def on_closing(self):
        """Handle window closing event"""
        # Unbind all mouse wheel events to prevent errors
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = GLUTCodeGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()