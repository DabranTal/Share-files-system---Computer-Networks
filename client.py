import socket
import sys
import time
from sys import platform
import os
import utils
import watchdog
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, PatternMatchingEventHandler
CREATE = 1
UPDATE = 3
DELETE = 4
FINISH = 1
NO_FINISH = 0
SEGMENT_SIZE = 1024
INT_IN_BITS = 32
BITS_ON_BYTE = 8

action_flag = 1


def on_created(event):
    print(f"hey, {event.src_path} has been created!")
    utils.update_folders(main_folder, event.src_path, s, user_id, CREATE)


def on_deleted(event):
    print(f"what the f**k! Someone deleted {event.src_path}!")
    utils.update_folders(main_folder, event.src_path, s, user_id, DELETE)


def on_modified(event):
    print(f"hey buddy, {event.src_path} has been modified")
    utils.update_folders(main_folder, event.src_path, s, user_id, UPDATE)


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
utils.build_folders_map(main_folder, my_directory, backslash, folder_path)


patterns = ["*"]
ignore_patterns = None
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified

path = "."
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, main_folder.path, go_recursively)

my_observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()


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
    utils.send_files(main_folder, main_folder.path, s, user_id)
    temp_user_id = s.recv(1024)
s.close()
