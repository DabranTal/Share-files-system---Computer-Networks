import random
import socket
import string
import sys
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 12345))
server.listen(0)
if len(sys.argv) != 2:
    exit()
while True:
    client_socket, client_address = server.accept()
    print('Connection from: ', client_address)
    user_id = client_socket.recv(100)
    if user_id.decode('utf-8') == 0:
        id_user = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(128))
        client_socket.send(str.encode(id_user))
    else
        clinet_socket.send(user_id)   
    print('Received: ', data)
    client_socket.send(data.upper())
    client_socket.close()
    print('Client disconnected')
