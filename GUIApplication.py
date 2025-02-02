# GUIApplication.py

"""
GUIApplication - Thread-Safe Tkinter GUI with Background Task Management

Usage:
1. Create application instance:
   app = GUIApplication(title="Your Title", width=800, height=600)

2. Add background tasks using callbacks:
   def your_task(exit_event):
       while not exit_event.is_set():
           # Your recurring logic here
           print("Task working...")
           exit_event.wait(1)  # Prefer over time.sleep()
           
   app.add_threaded_task(your_task)

3. Start the application:
   app.start()

Features:
- Automatic print() redirection to GUI text box
- Thread-safe background task management
- Built-in exit event handling
- Scrollable log window

Key Parameters:
- title: Window title (default: "GUI Logger")
- width: Window width in pixels (default: 400)
- height: Window height in pixels (default: 300)

Callback Requirements:
- Must accept exit_event as first parameter
- Should regularly check exit_event.is_set()
- Use exit_event.wait() instead of time.sleep()
- Avoid direct GUI operations in callbacks

Example Usage:
def sensor_reader(exit_event):
    while not exit_event.is_set():
        data = read_sensors()  # Your I/O operation
        print(f"Sensor value: {data}")
        exit_event.wait(0.5)

app = GUIApplication(title="Sensor Monitor")
app.add_threaded_task(sensor_reader)
app.start()

Important Notes:
- All GUI interactions must happen in main thread
- Callbacks should be CPU-friendly (use waits)
- System tray icon not included (pure console alternative available)
- Daemon threads auto-terminate when window closes
- Original sys.stdout restored on window close
"""

import sys
import threading
import queue
import tkinter as tk

class GUIApplication:
    def __init__(self, title="GUI Logger", width=400, height=300):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        
        self.exit_event = threading.Event()
        self.threads = []
        self._setup_gui()
        self._setup_stdout_redirect()
        
    def _setup_gui(self):
        """Initialize GUI components"""
        # Text area with scrollbar
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(expand=True, fill=tk.BOTH)
        
        self.scrollbar = tk.Scrollbar(self.text_frame)
        self.text_box = tk.Text(
            self.text_frame, 
            wrap=tk.WORD, 
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.text_box.yview)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_threaded_task(self, callback):
        """
        Add a background task that receives exit_event
        Usage: app.add_threaded_task(my_function)
        """
        def wrapped_callback():
            callback(self.exit_event)
            
        thread = threading.Thread(target=wrapped_callback, daemon=True)
        self.threads.append(thread)
        thread.start()

    def on_close(self):
        """Clean shutdown procedure"""
        self.exit_event.set()
        sys.stdout = self.original_stdout
        self.root.destroy()

    def start(self):
        """Start the application main loop"""
        self.root.mainloop()

    ## STDOUT TO GUI ###########################################################
    def _setup_stdout_redirect(self):
        """Configure print statement redirection"""
        self.message_queue = queue.Queue()
        self.original_stdout = sys.stdout
        
        sys.stdout = self  # Redirect stdout to this class instance
        self.root.after(100, self._process_queue)

    def write(self, message):
        """Handle stdout write operations"""
        self.message_queue.put(message)

    def flush(self):
        """Required for stdout compatibility"""
        pass

    def _process_queue(self):
        """Update GUI with queued messages from any thread"""
        while not self.message_queue.empty():
            msg = self.message_queue.get_nowait()
            self.text_box.insert(tk.END, msg)
            self.text_box.see(tk.END)
        self.root.after(100, self._process_queue)

# Example usage
if __name__ == "__main__":
    def example_task(exit_event):
        """User-provided callback function"""
        counter = 0
        while not exit_event.is_set():
            print(f"Task running... {counter}")
            counter += 1
            exit_event.wait(1)  # Sleep with exit check

    app = GUIApplication(title="Task Monitor", width=600, height=400)
    app.add_threaded_task(example_task)
    app.start()
