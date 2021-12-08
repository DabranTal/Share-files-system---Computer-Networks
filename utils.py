import socket
import sys
from socket import error as SocketError
from sys import platform
import os

CREATE = 1
UPDATE = 3
DELETE = 4
ADD_FOLDER = 5
FINISH = 1
NO_FINISH = 0
SEGMENT_SIZE = 1024
INT_IN_BITS = 32
BITS_ON_BYTE = 8


class Folder:
    path = None
    sub_folders = []
    files = []

    def __init__(self, cur_path):
        self.path = cur_path
        self.sub_folders = []
        self.files = []


class User_Dic:
    comp_id = ''
    folders_map = None
    actions = ''

    def __init__(self, user_comp):
        self.comp_id = user_comp
        self.folders_map = None
        self.actions = ''



def data_analysis(data):
    if b'stop' == data:
        return
    str_data = data.decode('utf-8')
    header_data = []
    for index in range(len(str_data) - 1, len(str_data), 1):
        header_data.append(str_data[index: index + 1])
    for index in range(len(str_data) - 2, len(str_data) - 1, 1):
        header_data.append(str_data[index: index + 1])
    for index in range(len(str_data) - 5, len(str_data) - 2, 3):
        header_data.append(str_data[index: index + 3])
    header_data[2] = 1000 - int(header_data[2])
    n = int(header_data[2])
    if 0 == n:
        header_data.append(None)
    else:
        for index in range(len(str_data) - 5 - n, len(str_data) - 5, n):
            header_data.append(str_data[index: index + n])
    backslash = get_backslash()
    if header_data[3][0] == backslash:
        header_data[3] = header_data[3][1:]
    # header_data[3] = header_data[3].replace(backslash, '')
    return header_data


def get_backslash():
    if platform == "win32":
        return '\\'
    else:
        return '/'


def get_relative_path(full_path, main_folder_path):
    main_path_len = len(main_folder_path)
    full_path_len = len(full_path)
    n = full_path_len - main_path_len
    if 0 == n:
        return None
    relative_array = ''
    j = 0
    for i in range(main_path_len, full_path_len):
        relative_array = relative_array + full_path[i]
        j = j + 1
    return relative_array


def create_sub_folders(folder_path, main_path, sock, user_id):
    relative_path = get_relative_path(folder_path, main_path)
    if relative_path is None:
        path_len = 0
        relative_path = ''
    else:
        path_len = len(relative_path)
    header = relative_path + str(1000 - path_len) + str(CREATE) + str(ADD_FOLDER)
    sock.send(str.encode(header))
    get_ack = sock.recv(1024)


def delete_from_cloud(folder, main_path):
    for file in folder.files:
        os.remove(file)
    for fold in folder.sub_folders:
        delete_from_cloud(fold, fold.path)
        os.rmdir(fold.path)


def upload_to_cloud(folder, main_path, sock, user_id):
    for fold in folder.sub_folders:
        create_sub_folders(fold.path, main_path, sock, user_id)
    for file in folder.files:
        send_file(file, main_path, sock)
    for fold in folder.sub_folders:
        upload_to_cloud(fold, main_path, sock, user_id)


def copy_data(src_map, src_path, dst_socket, user_id):
    upload_to_cloud(src_map, src_path, dst_socket, user_id)


def send_file(file, main_path, sock):
    relative_path = get_relative_path(file, main_path)
    if relative_path is None:
        path_len = 0
        relative_path = ''
    else:
        path_len = len(relative_path)
    header = relative_path + str(1000 - path_len) + str(CREATE) + str(CREATE)
    sock.send(str.encode(header))
    ans1 = sock.recv(1024)
    with open(file, 'rb') as g:
        reader = g.read(1024)
        while reader != b'':
            sock.send(reader)
            ans2 = sock.recv(1024)
            reader = g.read(1024)
        sock.send(b'stop')
    ans3 = sock.recv(1024)


def create_a_folder(folder_name, directory):
    path = os.path.join(directory, folder_name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def get_files(user_folder_path, sock):
    backslash = get_backslash()
    header = sock.recv(1024)
    sock.send(b'ack')
    print(header)
    while header != b'enough':
        header = data_analysis(header)
        if ADD_FOLDER == int(header[0]):
            create_a_folder(header[3], user_folder_path)
        else:
            file = None
            with open(user_folder_path + backslash + header[3], 'wb') as new_file:
                while file != b'stop':
                    file = sock.recv(1024)
                    sock.send(b'ack')
                    if b'stop' != file:
                        new_file.write(file)
                new_file.close()
        header = sock.recv(1024)
        sock.send(b'ack')


def is_this_path_exits(path):
    return os.path.exists(path)


def build_folders_map(folder, directory, backslash, folder_path):
    for file in directory:
        file_name, extension = os.path.splitext(file)
        if os.path.isdir(folder_path + backslash + file):
            folder.sub_folders.append(Folder(folder_path + backslash + file))
        else:
            folder.files.append((folder_path + backslash + file))
    if 0 < len(folder.sub_folders):
        for i in range(len(folder.sub_folders)):
            build_folders_map(folder.sub_folders[i], os.listdir(folder.sub_folders[i].path), backslash,
                              folder.sub_folders[i].path)