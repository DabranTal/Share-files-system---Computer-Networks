import socket
import sys
from sys import platform
import os
CREATE = 1
UPDATE = 3
DELETE = 4
FINISH = 1
NO_FINISH = 0
SEGMENT_SIZE = 1024
INT_IN_BITS = 32
BITS_ON_BYTE = 8


class Folder:
    path = None
    sub_folders =[]
    files = []

    def __init__(self, cur_path):
        self.path = cur_path
        self.sub_folders = []
        self.files = []


def data_analysis_2(data):
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
    header_data[3] = header_data[3].replace('\\', '')
    return header_data


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
        j = j+1
    return relative_array


def send_files(folder, main_path, sock, user_id):
    for f in folder.files:
        relative_path = get_relative_path(f, main_path)
        if relative_path is None:
            path_len = 0
            relative_path = ''
        else:
            path_len = len(relative_path)
        header = relative_path + str(1000-path_len) + str(CREATE) + str(CREATE)
        sock.send(user_id)
        ans1 = sock.recv(1024)
        sock.send(str.encode(header))
        ans2 = sock.recv(1024)
        with open(str(f), 'rb') as g:
            reader = g.read(1024)
            while reader != b'':
                sock.send(reader)
                reader = g.read(1024)
                ans3 = sock.recv(1024)
            sock.send(b'stop')
            g.close()
    ans4 = sock.recv(1024)
    print('enough')
    sock.send(b'enough')


def update_folders(to_change_path, main_path, sock, user_id, action):
    if CREATE == action:
        send_files(to_change_path, main_path, sock, user_id)
    elif DELETE == action:
        send_files(to_change_path, main_path, sock, user_id)
    elif UPDATE == action:
        send_files(to_change_path, main_path, sock, user_id)
        

def is_this_path_exits(path):
    return os.path.exists(path)


def build_folders_map(folder, directory, backslash, folder_path):
    for file in directory:
        file_name, extension = os.path.splitext(file)
        if '' == extension:
            folder.sub_folders.append(Folder(folder_path + backslash + file_name))
        else:
            folder.files.append((folder_path + backslash + file))
    for i in range(len(folder.sub_folders)):
        build_folders_map(folder.sub_folders[i], os.listdir(folder.sub_folders[i].path), backslash, folder.sub_folders[i].path)
