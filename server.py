
import random
import socket
import string
import sys
import utils
import os


def data_analysis(data):
    str_data = str(data)
    header_data = []
    for index in range(len(str_data) - 4, len(str_data), 4):
        header_data.append(str_data[index: index + 4])
    for index in range(len(str_data) - 5, len(str_data) - 4, 1):
        header_data.append(str_data[index: index + 1])
    for index in range(len(str_data) - 8, len(str_data) - 5, 3):
        header_data.append(str_data[index: index + 3])
    for index in range(len(str_data) - 40, len(str_data) - 8, 32):
        header_data.append(str_data[index: index + 32])
    n = int(header_data[3], 2)
    for index in range(len(str_data) - 40 - n, len(str_data) - 40, n):
        header_data.append(str_data[index: index + n])
    for index in range(0, len(str_data) - 40 - n, len(str_data) - 40 - n):
        header_data.append(str_data[index: index + len(str_data) - 40 - n])
    return header_data


def create_a_floder(userid, directory):
    path = os.path.join(directory, userid)
    os.mkdir(path)
    return path


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 12345))
server.listen(0)
if len(sys.argv) != 2:
    exit()
while True:
    client_socket, client_address = server.accept()
    print('Connection from: ', client_address)
    user_id = client_socket.recv(1024)
    if user_id.decode('utf-8') == '0':
        id_user = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(128))
        client_socket.send(str.encode(id_user))
        user_folder = create_a_floder(id_user, os.getcwd())
        header = client_socket.recv(1024)
        header = utils.data_analysis_2(header)
        print('file name: ', header[3])
        file = client_socket.recv(1024)
        with open(str(user_folder) + header[3], 'wb') as f:
            while file != '':
                f.write(file)
                file = client_socket.recv(1024)
            f.close()
    else:
        client_socket.send(user_id)
    print('\nReceived: ', user_id)
    client_socket.send(user_id.upper())
    client_socket.close()
    print('Client disconnected')
