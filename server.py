import socket
import sys
from sys import platform
import os
import utils
ADD_FOLDER = 1
ADD_FILE = 2
UPDATE_FILE = 3
DELETE_FILE = 4
FINISH = 1
NO_FINISH = 0
SEGMENT_SIZE = 1024
INT_IN_BITS = 32
BITS_ON_BYTE = 8


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


def send_files(folder, main_path, sock):
    for f in folder.files:
        relative_path = get_relative_path(f, main_path)
        if relative_path is None:
            path_len = 0
            relative_path = ''
        else:
            path_len = len(relative_path)
        to_send = relative_path + str(1000-path_len) + str(ADD_FOLDER) + str(ADD_FOLDER)
        sock.send(str.encode(to_send))
        with open(str(f), 'rb') as g:
            reader = g.read(1024)
            while reader != b'':
                sock.send(reader)
                reader = g.read(1024)
            sock.send(b'stop')
            g.close()
    sock.send(b'enough')


# Initialize all the variable we got as arguments
ip_server = sys.argv[1]
port_server = sys.argv[2]
folder_path = sys.argv[3]
time_temp = sys.argv[4]
# Set default id for case the is isn't define by an argument
user_id = 0
if len(sys.argv) == 6:
    user_id = sys.argv[5]
# Check which platform the user using to define how to apart folders in the files path
if platform == "win32":
    backslash = '\\'
else:
    backslash = '/'
my_directory = os.listdir(folder_path)
main_folder = utils.Folder(folder_path)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
s.connect((ip_server, int(port_server)))
# Make sure the server know who am i
s.send(str.encode(str(user_id)))
temp_user_id = s.recv(1024)
# If the ID doesnt exist get new id and build folders map
if temp_user_id != user_id:
    utils.build_folders_map(main_folder, my_directory, backslash, folder_path)
    user_id = temp_user_id
    # Start sync folders map
    utils.build_folders_map(main_folder, my_directory, backslash, folder_path)
    send_files(main_folder, main_folder.path, s)
    temp_user_id = s.recv(1024)
# TO DO:
s.send(b'316222512 & 316040898')
data = s.recv(100)
print("Server sent: ", data)
s.close()
