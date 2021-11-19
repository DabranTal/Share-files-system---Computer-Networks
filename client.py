import socket
import sys
from sys import platform
import os

class Folder:
    path = None
    sub_folders =[]
    files = []

    def __init__(self, cur_path):
        self.path = cur_path

def is_this_path_exits(path):
    return os.path.exists(path)

def build_folders_map(folder):
    for file in my_directory:
        file_name, extension = os.path.splitext(file)
        if '' == extension:
            folder.sub_folders.append(Folder(folder_path + backslash + file_name))
        else:
            folder.files_in_directory.append((folder_path + backslash + file))
    for sub_fold in folder.sub_folders:
        build_folders_map(sub_fold)

# Initialize all the variable we got as arguments
ip_server = sys.argv[1]
port_server = sys.argv[2]
folder_path = sys.argv[3]
time_temp = sys.argv[4]
# Set default id for case the is isn't define by an argument
user_id = 0
if len(sys.argv) == 5:
    user_id = sys.argv[5]
# Check which platform the user using to define how to apart folders in the files path
if platform == "win32":
    backslash = '\\'
else:
    backslash = '/'
my_directory = os.listdir(folder_path)
main_folder = Folder(folder_path)
build_folders_map (main_folder)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip_server, int(port_server)))
# Make sure the server know who am i. If the id doesnt exist get new id
s.send(str.encode(user_id))
user_id = s.recv(100)
# TO DO:
s.send(b'316222512 & 316040898')
data = s.recv(100)
print("Server sent: ", data)
s.close()
