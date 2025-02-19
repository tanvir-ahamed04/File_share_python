import socket
import os

def send_file(filename, host, port):
    # Ensure the file exists
    if not os.path.exists(filename):
        print(f"File '{filename}' not found!")
        return

    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")

    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    # Open the file and send it to the client
    with open(filename, 'rb') as file:
        print(f"Sending '{filename}'...")
        while (chunk := file.read(1024)):
            client_socket.send(chunk)
    
    print(f"File '{filename}' sent successfully!")
    client_socket.close()
    server_socket.close()

# Define the host and port to bind the server
HOST = '0.0.0.0'  # Bind to all network interfaces
PORT = 12345  # Choose a port number

# Specify the file to send
filename = "example.txt"  # Replace with your file name
send_file(filename, HOST, PORT)
