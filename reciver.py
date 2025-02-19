import socket

def receive_file(server_ip, server_port, output_filename):
    # Set up the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    print(f"Connected to {server_ip}:{server_port}...")

    # Open the output file to write the received data
    with open(output_filename, 'wb') as file:
        print("Receiving file...")
        while (chunk := client_socket.recv(1024)):
            file.write(chunk)
    
    print(f"File '{output_filename}' received successfully!")
    client_socket.close()

# Define the server IP and port (make sure it matches the server)
SERVER_IP = '192.168.1.10'  # Replace with the IP of the server (sender)
SERVER_PORT = 12345  # The same port used by the server

# Output filename to save the received file
output_filename = "received_example.txt"  # Change this as needed

receive_file(SERVER_IP, SERVER_PORT, output_filename)
