import random
import socket
import string
import sys
import utils
import os
ADD_FOLDER = 5


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
    backslash = utils.get_backslash()
    user_id = client_socket.recv(1024)
    if user_id.decode('utf-8') == '0':
        id_user = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(128))
        client_socket.send(str.encode(id_user))
        # Create main user folder
        user_folder_path = create_a_folder(id_user, os.getcwd())
        header = client_socket.recv(1024)
        while header != b'enough':
            header = utils.data_analysis_2(header)
            if ADD_FOLDER == int(header[0]):
                client_socket.send(b'ack')
                create_a_folder(header[3], user_folder_path)
            else:
                file = None
                with open(user_folder_path + backslash + header[3], 'wb') as new_file:
                    while file != b'stop':
                        client_socket.send(b'ack')
                        file = client_socket.recv(1024)
                        if b'stop' != file:
                            new_file.write(file)
                    new_file.close()
                    client_socket.send(b'ack')
            header = client_socket.recv(1024)
    else:
        client_socket.send(user_id)
    client_socket.close()
    print('Client disconnected')
