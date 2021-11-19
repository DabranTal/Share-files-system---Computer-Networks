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
    relative_path = get_relative_path(folder.path, main_path)
    if relative_path is None:
        path_len = 0
        relative_path = ''
    else:
        path_len = len(relative_path) * BITS_ON_BYTE
    for f in folder.files:
        bits_to_read = SEGMENT_SIZE - path_len - INT_IN_BITS - BITS_ON_BYTE
        file = open(f)
        were_read = file.read(bits_to_read)
        to_send = were_read + relative_path + str(path_len) + str(ADD_FOLDER) + str(ADD_FILE)
        to_send = str.encode(to_send)
        a = utils.data_analysis(to_send)
        x = 8



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
main_folder = utils.Folder(folder_path)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
utils.build_folders_map(main_folder, my_directory, backslash, folder_path)
send_files(main_folder, main_folder.path, s)
s.connect((ip_server, int(port_server)))
# Make sure the server know who am i
s.send(str.encode(user_id))
temp_user_id = s.recv(1024)
# If the ID doesnt exist get new id and build folders map
if temp_user_id != user_id:
    utils.build_folders_map(main_folder, my_directory, backslash, folder_path)
    user_id = temp_user_id
    # Start sync folders map
    send_files(main_folder, main_folder.path, s)
    s.send(str.encode())
    temp_user_id = s.recv(1024)
# TO DO:
s.send(b'316222512 & 316040898')
data = s.recv(100)
print("Server sent: ", data)
s.close()
