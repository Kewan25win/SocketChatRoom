import socket
import threading
import sqlite3
import hashlib

#users = {"kewan": "123", "soran": "123", "hezhin": "123"}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 6000
server_address = (host, port)
server.bind(server_address)
server.listen()
print("Server waiting clints to connect")

conn = sqlite3.connect("users.db",check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)""")
conn.commit()

def hash_password(password):
    hash_object = hashlib.sha256()
    hash_object.update(password.encode("utf-8"))
    hex_digest = hash_object.hexdigest()
    return hex_digest
def add_user(username, password):
    hashed_password = hash_password(password)
    c.execute(f"INSERT INTO users VALUES ('{username}', '{hashed_password}')")
    conn.commit()
def username_exist(username):
    c.execute(f"SELECT * FROM users WHERE username='{username}'")
    return c.fetchone() is not None

client_sockets = []
logged_sockets={}

def client_thread(client_socket):

    client_message = client_socket.recv(1024).decode("utf-8")
    parts = client_message.split(",")
    command = parts[0]
    #global username
    username = parts[1]
    password = parts[2]

    try:

        if command == "login":
            hashed_password = hash_password(password)
            c.execute(
                f"SELECT * FROM users WHERE username='{username}' AND password='{hashed_password}'"
            )
            if c.fetchone() is not None:
                welcome_message = f"Welcome to the chat {username}!"
                client_socket.send(welcome_message.encode("utf-8"))
                #session(username)

                logged_sockets[username]=client_socket
                print(username," Connected to the Chat Room")

            else:
                error_message = "Invalid username or password"
                client_socket.send(error_message.encode("utf-8"))
                client_socket.close()


        elif command == "signup":
            if username_exist(username):
                error_message = "Username already taken!"
                client_socket.send(error_message.encode("utf-8"))
            else:
                add_user(username, password)
                welcome_message = f"Welcome to the chat {username}!"
                client_socket.send(welcome_message.encode("utf-8"))
                logged_sockets[username]=client_socket
                print(username," Connected to the Chat Room")


        else:
            error_message = "Invalid command"
            client_socket.send(error_message.encode("utf-8"))
            client_socket.close()

    except :
        error_message = "Invalid command"
        client_socket.send(error_message.encode("utf-8"))
        client_socket.close()
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                client_sockets.remove(client_socket)
                client_socket.close()
                break
            elif message.startswith('@'):
                    # Private message format: @recipient_username:message
                    recipient, private_message = message.split(':', 1)
                    print("Private Message")
                    send_private_message(username, recipient[1:], private_message)
            else:
                    broadcast(f"{username}: {message}", client_socket)
        except:
            client_sockets.remove(client_socket)
            client_socket.close()
            break
def broadcast(message, sender_socket):
    for socket in client_sockets:
        if socket != sender_socket:
            socket.send(message.encode("utf-8"))
def send_private_message(sender, recipient, message):
   try:
    if recipient in logged_sockets:
        recipient_socket = logged_sockets[recipient]
        private_message = "[Private from {}]: {}".format(sender, message)
        recipient_socket.send(private_message.encode('utf-8'))
    else:
        sender_socket = logged_sockets[sender]
        error_message = "[Server]: User {} not found or offline.".format(recipient)
        sender_socket.send(error_message.encode('utf-8'))
   except:
        sender_socket = logged_sockets[sender]
        error_message = "[Server]: User {} is offline now.".format(recipient)
        sender_socket.send(error_message.encode('utf-8'))


while True:
    client_socket, addr = server.accept()
    global address
    address=addr
    #print(address)
    client_sockets.append(client_socket)
    threading.Thread(target=client_thread, args=(client_socket,)).start()
