import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math

points = []
image_ref = None
canvas_image_id = None
current_mode = "polygon"  # polygon, quads, lines, line_loop, circle
circle_center = None
circle_radius_point = None
circle_preview_id = None

def load_image():
    global image_ref, canvas_image_id
    
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"), ("All files", "*.*")]
    )
    
    if not file_path:
        return
    
    try:
        # Load and resize image to fit canvas
        img = Image.open(file_path)
        img = img.resize((600, 600), Image.Resampling.LANCZOS)
        image_ref = ImageTk.PhotoImage(img)
        
        # Remove old image if exists
        if canvas_image_id:
            canvas.delete(canvas_image_id)
        
        # Display image on canvas
        canvas_image_id = canvas.create_image(0, 0, anchor=tk.NW, image=image_ref)
        canvas.tag_lower(canvas_image_id)  # Put image behind points/lines
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {str(e)}")

def click(event):
    global circle_center, circle_radius_point, circle_preview_id
    
    x, y = event.x, event.y
    
    if current_mode == "circle":
        if circle_center is None:
            # First click: set center
            circle_center = (x, y)
            r = 3
            canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue", tags="point")
            canvas.create_text(x, y-15, text="Center", fill="blue", tags="point")
        elif circle_radius_point is None:
            # Second click: set radius
            circle_radius_point = (x, y)
            r = 3
            canvas.create_oval(x-r, y-r, x+r, y+r, fill="green", tags="point")
            # Draw the final circle
            radius = ((x - circle_center[0])**2 + (y - circle_center[1])**2)**0.5
            if circle_preview_id:
                canvas.delete(circle_preview_id)
            circle_preview_id = canvas.create_oval(
                circle_center[0] - radius, circle_center[1] - radius,
                circle_center[0] + radius, circle_center[1] + radius,
                outline="green", width=2, tags="circle"
            )
        else:
            # Reset for new circle
            circle_center = (x, y)
            circle_radius_point = None
            canvas.delete("circle")
            if circle_preview_id:
                canvas.delete(circle_preview_id)
                circle_preview_id = None
            r = 3
            canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue", tags="point")
            canvas.create_text(x, y-15, text="Center", fill="blue", tags="point")
    else:
        # Regular point selection for other modes
        points.append((x, y))
        
        # Draw point (with tag so it stays on top)
        r = 3
        canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", tags="point")
        
        # Draw line to previous point (for visual feedback)
        if len(points) > 1 and current_mode in ["lines", "line_loop"]:
            canvas.create_line(points[-2][0], points[-2][1], x, y, tags="line")
        elif len(points) > 1 and current_mode == "polygon":
            canvas.create_line(points[-2][0], points[-2][1], x, y, tags="line")
        elif len(points) > 1 and current_mode == "quads" and len(points) % 4 == 0:
            # Draw quad when 4 points are selected
            if len(points) >= 4:
                p1 = points[-4]
                p2 = points[-3]
                p3 = points[-2]
                p4 = points[-1]
                canvas.create_line(p1[0], p1[1], p2[0], p2[1], tags="line")
                canvas.create_line(p2[0], p2[1], p3[0], p3[1], tags="line")
                canvas.create_line(p3[0], p3[1], p4[0], p4[1], tags="line")
                canvas.create_line(p4[0], p4[1], p1[0], p1[1], tags="line")

def convert_coords(x, y):
    """Convert screen coordinates to OpenGL coordinates"""
    try:
        x_min = float(x_min_entry.get())
        x_max = float(x_max_entry.get())
        y_min = float(y_min_entry.get())
        y_max = float(y_max_entry.get())
    except ValueError:
        return None, None
    
    canvas_width = 600
    canvas_height = 600
    
    # Normalize x from [0, canvas_width] to [x_min, x_max]
    gl_x = x_min + (x / canvas_width) * (x_max - x_min)
    # Normalize y from [0, canvas_height] to [y_max, y_min] (flip Y axis)
    gl_y = y_max - (y / canvas_height) * (y_max - y_min)
    
    return gl_x, gl_y

def generate_code():
    global circle_center, circle_radius_point
    
    try:
        x_min = float(x_min_entry.get())
        x_max = float(x_max_entry.get())
        y_min = float(y_min_entry.get())
        y_max = float(y_max_entry.get())
    except ValueError:
        output.delete(1.0, tk.END)
        output.insert(1.0, "// Invalid axis values. Please enter numbers.")
        output.see(1.0)
        return
    
    if x_min >= x_max or y_min >= y_max:
        output.delete(1.0, tk.END)
        output.insert(1.0, "// Invalid axis range. Min must be less than max.")
        output.see(1.0)
        return
    
    code = ""
    
    if current_mode == "circle":
        if circle_center is None or circle_radius_point is None:
            output.delete(1.0, tk.END)
            output.insert(1.0, "// Please select center and radius point for circle")
            output.see(1.0)
            return
        
        # Calculate radius in screen coordinates
        radius_screen = ((circle_radius_point[0] - circle_center[0])**2 + 
                        (circle_radius_point[1] - circle_center[1])**2)**0.5
        
        # Convert center to OpenGL coordinates
        center_x, center_y = convert_coords(circle_center[0], circle_center[1])
        if center_x is None:
            output.delete(1.0, tk.END)
            output.insert(1.0, "// Invalid axis values. Please enter numbers.")
            output.see(1.0)
            return
        
        # Calculate radius in OpenGL coordinates
        canvas_width = 600
        canvas_height = 600
        radius_gl = (radius_screen / canvas_width) * (x_max - x_min)
        
        # Generate circle using the specified format
        code = f"float cx = {center_x:.2f}f, cy = {center_y:.2f}f;  // center\n\n"
        code += f"    float r = {radius_gl:.2f}f;               // radius\n\n"
        code += "    int i;\n\n"
        code += "    glColor3f(1.0, 1.0, 0.0);\n"
        code += "    glBegin(GL_POLYGON);\n"
        code += "    for (i = 0; i < 100; i++)\n"
        code += "    {\n"
        code += "        float angle = 2 * 3.1416f * i / 100;\n"
        code += "        glVertex2f(cx + r * cos(angle),\n"
        code += "                   cy + r * sin(angle));\n"
        code += "    }\n"
        code += "    glEnd();"
        
    elif current_mode == "polygon":
        if len(points) < 3:
            output.delete(1.0, tk.END)
            output.insert(1.0, "// Need at least 3 points for polygon")
            output.see(1.0)
            return
        
        code = "glBegin(GL_POLYGON);\n"
        for x, y in points:
            gl_x, gl_y = convert_coords(x, y)
            if gl_x is None:
                output.delete(1.0, tk.END)
                output.insert(1.0, "// Invalid axis values. Please enter numbers.")
                output.see(1.0)
                return
            code += f"    glVertex2f({gl_x:.2f}f, {gl_y:.2f}f);\n"
        code += "glEnd();"
        
    elif current_mode == "quads":
        if len(points) < 4:
            output.delete(1.0, tk.END)
            output.insert(1.0, "// Need at least 4 points for quads (points must be multiple of 4)")
            output.see(1.0)
            return
        
        if len(points) % 4 != 0:
            output.delete(1.0, tk.END)
            output.insert(1.0, f"// Need multiple of 4 points for quads. Currently have {len(points)} points.")
            output.see(1.0)
            return
        
        code = "glBegin(GL_QUADS);\n"
        for i in range(0, len(points), 4):
            for j in range(4):
                x, y = points[i + j]
                gl_x, gl_y = convert_coords(x, y)
                if gl_x is None:
                    output.delete(1.0, tk.END)
                    output.insert(1.0, "// Invalid axis values. Please enter numbers.")
                    output.see(1.0)
                    return
                code += f"    glVertex2f({gl_x:.2f}f, {gl_y:.2f}f);\n"
        code += "glEnd();"
        
    elif current_mode == "lines":
        if len(points) < 2:
            output.delete(1.0, tk.END)
            output.insert(1.0, "// Need at least 2 points for lines")
            output.see(1.0)
            return
        
        if len(points) % 2 != 0:
            output.delete(1.0, tk.END)
            output.insert(1.0, f"// Need even number of points for lines. Currently have {len(points)} points.")
            output.see(1.0)
            return
        
        code = "glBegin(GL_LINES);\n"
        for i in range(0, len(points), 2):
            for j in range(2):
                if i + j < len(points):
                    x, y = points[i + j]
                    gl_x, gl_y = convert_coords(x, y)
                    if gl_x is None:
                        output.delete(1.0, tk.END)
                        output.insert(1.0, "// Invalid axis values. Please enter numbers.")
                        output.see(1.0)
                        return
                    code += f"    glVertex2f({gl_x:.2f}f, {gl_y:.2f}f);\n"
        code += "glEnd();"
        
    elif current_mode == "line_loop":
        if len(points) < 2:
            output.delete(1.0, tk.END)
            output.insert(1.0, "// Need at least 2 points for line loop")
            output.see(1.0)
            return
        
        code = "glBegin(GL_LINE_LOOP);\n"
        for x, y in points:
            gl_x, gl_y = convert_coords(x, y)
            if gl_x is None:
                output.delete(1.0, tk.END)
                output.insert(1.0, "// Invalid axis values. Please enter numbers.")
                output.see(1.0)
                return
            code += f"    glVertex2f({gl_x:.2f}f, {gl_y:.2f}f);\n"
        code += "glEnd();"
    
    output.delete(1.0, tk.END)
    output.insert(1.0, code)
    output.see(1.0)  # Scroll to top to show the code
    
    # Scroll the main window to show the output area
    scroll_canvas.update_idletasks()
    # Get the y position of the output frame and scroll to it
    output_frame.update_idletasks()
    output_y = output_frame.winfo_y()
    canvas_height = scroll_canvas.winfo_height()
    scroll_position = min(1.0, (output_y - 50) / max(1, scrollable_content.winfo_height() - canvas_height))
    scroll_canvas.yview_moveto(max(0.0, scroll_position))

def clear():
    global points, circle_center, circle_radius_point, circle_preview_id
    points.clear()
    circle_center = None
    circle_radius_point = None
    if circle_preview_id:
        canvas.delete(circle_preview_id)
        circle_preview_id = None
    # Delete only points, lines, and circles, keep image
    canvas.delete("point")
    canvas.delete("line")
    canvas.delete("circle")
    canvas.delete("circle_preview")
    output.delete(1.0, tk.END)

def set_mode(mode):
    global current_mode, circle_center, circle_radius_point, circle_preview_id
    current_mode = mode
    # Reset circle selection when switching modes
    if mode != "circle":
        circle_center = None
        circle_radius_point = None
        if circle_preview_id:
            canvas.delete(circle_preview_id)
            circle_preview_id = None
    # Update button states
    mode_map = {
        "polygon": "Polygon",
        "quads": "Quads",
        "lines": "Lines",
        "line_loop": "Line Loop",
        "circle": "Circle"
    }
    for btn in mode_buttons:
        if btn["text"] == mode_map.get(mode, ""):
            btn.config(relief=tk.SUNKEN, state=tk.DISABLED)
        else:
            btn.config(relief=tk.RAISED, state=tk.NORMAL)

root = tk.Tk()
root.title("Draw Shape → Get GLUT Code")
root.geometry("650x600")

# Top frame for image loading and generate button
top_frame = tk.Frame(root)
top_frame.pack(pady=5)

tk.Button(top_frame, text="Load Image", command=load_image).pack(side=tk.LEFT, padx=5)
tk.Button(top_frame, text="Generate Vertices", command=generate_code, width=18).pack(side=tk.LEFT, padx=5)

# Mode selection frame
mode_frame = tk.LabelFrame(root, text="Primitive Type", padx=5, pady=5)
mode_frame.pack(pady=5)

mode_buttons = []
modes = [
    ("Polygon", "polygon"),
    ("Quads", "quads"),
    ("Lines", "lines"),
    ("Line Loop", "line_loop"),
    ("Circle", "circle")
]

for i, (label, mode) in enumerate(modes):
    btn = tk.Button(
        mode_frame, 
        text=label, 
        command=lambda m=mode: set_mode(m),
        width=12,
        relief=tk.RAISED
    )
    btn.grid(row=0, column=i, padx=2)
    mode_buttons.append(btn)

# Set default mode
set_mode("polygon")

# Axis configuration frame
axis_frame = tk.LabelFrame(root, text="Axis Configuration", padx=5, pady=5)
axis_frame.pack(pady=5)

tk.Label(axis_frame, text="X Min:").grid(row=0, column=0, padx=5)
x_min_entry = tk.Entry(axis_frame, width=10)
x_min_entry.insert(0, "-1.0")
x_min_entry.grid(row=0, column=1, padx=5)

tk.Label(axis_frame, text="X Max:").grid(row=0, column=2, padx=5)
x_max_entry = tk.Entry(axis_frame, width=10)
x_max_entry.insert(0, "1.0")
x_max_entry.grid(row=0, column=3, padx=5)

tk.Label(axis_frame, text="Y Min:").grid(row=1, column=0, padx=5)
y_min_entry = tk.Entry(axis_frame, width=10)
y_min_entry.insert(0, "-1.0")
y_min_entry.grid(row=1, column=1, padx=5)

tk.Label(axis_frame, text="Y Max:").grid(row=1, column=2, padx=5)
y_max_entry = tk.Entry(axis_frame, width=10)
y_max_entry.insert(0, "1.0")
y_max_entry.grid(row=1, column=3, padx=5)

# Create scrollable frame for canvas and output
scrollable_frame = tk.Frame(root)
scrollable_frame.pack(fill=tk.BOTH, expand=True)

# Create canvas for scrolling
scroll_canvas = tk.Canvas(scrollable_frame, bg="white")
scrollbar_main = tk.Scrollbar(scrollable_frame, orient=tk.VERTICAL, command=scroll_canvas.yview)
scrollable_content = tk.Frame(scroll_canvas)

scrollable_content.bind(
    "<Configure>",
    lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
)

scroll_canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
scroll_canvas.configure(yscrollcommand=scrollbar_main.set)

scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar_main.pack(side=tk.RIGHT, fill=tk.Y)

# Bind mousewheel to scroll (works on Windows)
def _on_mousewheel(event):
    scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)
# Also bind for Linux
scroll_canvas.bind_all("<Button-4>", lambda e: scroll_canvas.yview_scroll(-1, "units"))
scroll_canvas.bind_all("<Button-5>", lambda e: scroll_canvas.yview_scroll(1, "units"))

# Image canvas inside scrollable content
canvas = tk.Canvas(scrollable_content, width=600, height=600, bg="white")
canvas.pack(pady=5)
canvas.bind("<Button-1>", click)

def on_mouse_move(event):
    """Preview circle radius while moving mouse after selecting center"""
    global circle_preview_id
    if current_mode == "circle" and circle_center is not None and circle_radius_point is None:
        x, y = event.x, event.y
        radius = ((x - circle_center[0])**2 + (y - circle_center[1])**2)**0.5
        if circle_preview_id:
            canvas.delete(circle_preview_id)
        circle_preview_id = canvas.create_oval(
            circle_center[0] - radius, circle_center[1] - radius,
            circle_center[0] + radius, circle_center[1] + radius,
            outline="cyan", width=1, dash=(5, 5), tags="circle_preview"
        )

canvas.bind("<Motion>", on_mouse_move)

# Output frame with label - positioned right after the image
output_frame = tk.LabelFrame(scrollable_content, text="Generated Code", padx=5, pady=5)
output_frame.pack(pady=5, padx=10, fill=tk.X)

output = tk.Text(output_frame, height=10, width=80, wrap=tk.WORD, font=("Courier", 10))
output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Add scrollbar for output text
output_scrollbar = tk.Scrollbar(output_frame, orient=tk.VERTICAL, command=output.yview)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output.config(yscrollcommand=output_scrollbar.set)

btn_frame = tk.Frame(scrollable_content)
btn_frame.pack(pady=10)

generate_btn = tk.Button(btn_frame, text="Generate Vertices", command=generate_code, width=20, height=2)
generate_btn.pack(side=tk.LEFT, padx=10)

clear_btn = tk.Button(btn_frame, text="Clear Points", command=clear, width=20, height=2)
clear_btn.pack(side=tk.LEFT, padx=10)

root.mainloop()
