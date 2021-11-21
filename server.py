
import random
import socket
import string
import sys
import utils
import os
ADD_FOLDER = 5


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


def create_a_folder(folder_name, directory):
    path = os.path.join(directory, folder_name)
    os.mkdir(path)
    return path


def upload_files_to_folder(file_name, folder_path, got_from_recv):
    backslash = utils.get_backslash()
    with open(folder_path + backslash + file_name, 'wb') as new_file:
        while got_from_recv != b'stop':
            new_file.write(got_from_recv)
            got_from_recv = client_socket.recv(1024)
            client_socket.send(b'ack')
        new_file.close()
        client_socket.send(b'ack')


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server.bind(('', int(sys.argv[1])))
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
        # Create main user folder
        user_folder_path = create_a_folder(id_user, os.getcwd())
        header = client_socket.recv(1024)
        client_socket.send(b'ack')
        while header != b'enough':
            header = utils.data_analysis_2(header)
            if ADD_FOLDER == int(header[0]):
                while b'stop' != header:
                    print('i have got here\n',header,'\n')
                    create_a_folder(header[3], user_folder_path)
                    header = client_socket.recv(1024)
                    client_socket.send(b'ack')
                    if b'stop' != header:
                        header = utils.data_analysis_2(header)
            else:
                client_socket.send(b'ack')
                print('i have got here\n',header,'\n')
                file = client_socket.recv(1024)
                client_socket.send(b'ack')
                upload_files_to_folder(header[3], user_folder_path, file)
            header = client_socket.recv(1024)
            client_socket.send(b'ack')

    else:
        client_socket.send(user_id)
    print('\nReceived: ', user_id)
    client_socket.send(user_id.upper())
    client_socket.close()
    print('Client disconnected')
