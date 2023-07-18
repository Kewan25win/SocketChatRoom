import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext, END
import socket
import threading
import sqlite3

#Connect to the server
def connect():
    host = '127.0.0.1'
    port = 6000
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
def login():
    try:
        connect()
        username=username_entry.get().strip()
        password=password_entry.get().strip()
        global client_socket
        #validate the username and password
        if not username or not password:
            error_label.config(text="Username or password cannot be blank!!")
            return
        else:
            command="login"
            global login_name
            login_name=username
            message = f'{command},{username},{password}'
            client_socket.send(message.encode('utf-8'))

            server_response = client_socket.recv(1024).decode('utf-8')

            if server_response=="Invalid username or password":
                error_label.config(text=server_response)
                return
            else:
                login_window.destroy()
                chat_window(server_response)
    except :
        messagebox.showerror("Error", "کێشەی سێرڤەر")
def getMembers():
    conn = sqlite3.connect("users.db",check_same_thread=False)
    cursor = conn.cursor()
    global login_name
    cursor.execute('SELECT * FROM users WHERE username != ?', (login_name,))
    # Fetch all rows from the query result
    rows = cursor.fetchall()
    # Close the database connection
    conn.close()
    return rows
def signup():
    try:
        connect()
        username=username_entry.get().strip()
        password=password_entry.get().strip()
        global client_socket
        if not username or not password:
            error_label.config(text="Username or password cannot be blank!!")
            return
        else:
            command="signup"
            message = f'{command},{username},{password}'
            global login_name
            login_name=username
            client_socket.send(message.encode('utf-8'))
            server_response = client_socket.recv(1024).decode('utf-8')

            if server_response=="Username already taken!":
                error_label.config(text="ئەم بەکارهێنەر داخڵکراوە!")
                return
            else:
                login_window.destroy()
                chat_window(message)
    except :
        messagebox.showerror("Error", "کێشەی سێرڤەر")
#list box even
def selected_item_event(event):
    global members_listbox
    selected_item = members_listbox.get(members_listbox.curselection())
    #member="kewan"
    member="@"+selected_item+":"
    message_entry.insert(tk.END,member)
    #private_chat_window(selected_item)
def close_program():
    global client_socket
    client_socket.close()
    global chat_win
    chat_win.destroy()
def chat_window(message):
    global content_text
    #print(message)
    # Create a new Tkinter window
    global chat_win
    chat_win = tk.Tk()
    chat_win.title("ژووری چاتی کێوان")

    # Create a frame for the chat members list
    members_frame = tk.Frame(chat_win, width=100)
    members_frame.pack(side=tk.RIGHT, fill=tk.Y)
    # Create a label for the chat members list
    members_label = tk.Label(members_frame, text="ئەندامەکان")
    members_label.pack()

    # Create a scrollable list of chat members
    global members_listbox
    members_listbox = tk.Listbox(members_frame,justify='center')
    members_listbox.pack(fill=tk.BOTH, expand=True)
    members=getMembers()

    members_listbox.bind("<<ListboxSelect>>", selected_item_event)

    for value in members:
        members_listbox.insert(tk.END, value[0])

    # Create a frame for the chat content
    content_frame = tk.Frame(chat_win)
    content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create a scrollable text widget for the chat content
    global content_text
    content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
    content_text.pack(fill=tk.BOTH, expand=True)

    # Create a frame for the message box and send button
    message_frame = tk.Frame(chat_win)
    message_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Create an entry field for typing messages
    global message_entry
    message_entry = tk.Text(message_frame, height=3)
    message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    #message_entry.bind("<Return>", send_message())  # Bind the <Return> event
    message_entry.bind("<Return>", lambda event: send_message())  # Bind the <Return> event

    # Create a send button
    send_button = tk.Button(message_frame, text="ناردن", command=send_message)
    send_button.pack(side=tk.RIGHT,fill='x', expand=True)


    # Start the Tkinter event loop

    def receive_thread():
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                #print(message)
                content_text.insert(tk.END,message+"\n")
            except:
                client_socket.close()
                break


    threading.Thread(target=receive_thread).start()

    chat_win.protocol("WM_DELETE_WINDOW", close_program)
    chat_win.mainloop()
def send_message():
    global message_entry
    global client_socket
    message = message_entry.get("1.0", END).strip()
    if message:
        client_socket.send(message.encode('utf-8'))
        content_text.insert(tk.END, "You: " + message + "\n")
        message_entry.delete("1.0", END)
    #Center Window
def center_window(login_window, width, height):
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    login_window.geometry(f"{width}x{height}+{x}+{y}")

try:
    #Connect to the Server

    #login method
    # Open Login Window
    login_window = tk.Tk()
    login_window.title("بەخێربێن بۆ چاتی کێوان")

    # Set the window size
    window_width = 400
    window_height = 200

    #position login screen to center of the screen
    center_window(login_window, window_width, window_height)

    # Create a username label and entry field
    username_label = tk.Label(login_window, text="ناوی بەکارهێنەر:")
    username_label.pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    # Create a password label and entry field
    password_label = tk.Label(login_window, text="تێپەڕەوشە:")
    password_label.pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    # Create a login button
    login_button = tk.Button(login_window, text="داخڵبوون", command=login)
    login_button.pack()

    # Create a signup button
    signup_button = tk.Button(login_window, text="خۆتۆمارکردن", command=signup)
    signup_button.pack()

    error_label = tk.Label(login_window, fg="red")
    error_label.pack()

    # Start the Tkinter event loop
    login_window.mainloop()
except :
      messagebox.showerror("Error", "کێشەی سێرڤەر")
