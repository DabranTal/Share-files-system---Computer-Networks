import socket
import sys
from sys import platform
import os
ADD_FOLDER = 0x0001
ADD_FILE = 0x0010
UPDATE_FILE = 0x0100
DELETE_FILE = 0x1000
SEGMENT_SIZE = 1024


class Folder:
    path = None
    sub_folders =[]
    files = []

    def __init__(self, cur_path):
        self.path = cur_path
        self.sub_folders =[]
        self.files =[]

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
