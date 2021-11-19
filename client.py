import socket
import sys
from sys import platform
import os
import utils


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
s.connect((ip_server, int(port_server)))
# Make sure the server know who am i
s.send(str.encode(user_id))
temp_user_id = s.recv(100)
# If the ID doesnt exist get new id and build folders map
if temp_user_id != user_id:
    utils.build_folders_map(main_folder, my_directory, backslash, folder_path)
    user_id = temp_user_id
    # Start sync folders map
    s.send(str.encode())
    temp_user_id = s.recv(100)
# TO DO:
s.send(b'316222512 & 316040898')
data = s.recv(100)
print("Server sent: ", data)
s.close()
