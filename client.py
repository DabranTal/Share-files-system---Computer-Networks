import socket
import sys
from sys import platform
import os

def is_this_path_exits(path):
    return os.path.exists(path)

def build_folders_map(path):
    #TO DO BUILD FOLDER MAP

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
sub_directories = []
files_in_directory = []
for file in my_directory:
    file_name, extension = os.path.splitext(file)
    if '' == extension:
        sub_directories.append(folder_path + backslash + file_name)
    else:
        files_in_directory.append((folder_path + backslash + file))
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
