import socket
import sys
from sys import platform
import os
import utils


class Folder:
    path = None
    sub_folders =[]
    files = []

    def __init__(self, cur_path):
        self.path = cur_path
        self.sub_folders =[]
        self.files =[]


def is_this_path_exits(path):
    return os.path.exists(path)


def build_folders_map(folder, directory, backslash, folder_path):
    for file in directory:
        file_name, extension = os.path.splitext(file)
        if '' == extension:
            folder.sub_folders.append(utils.Folder(folder_path + backslash + file_name))
        else:
            folder.files.append((folder_path + backslash + file))
    for i in range(len(folder.sub_folders)):
        build_folders_map(folder.sub_folders[i], os.listdir(folder.sub_folders[i].path))
