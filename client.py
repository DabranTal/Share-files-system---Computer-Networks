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

def check_if_exist_path(main_folder ,event):
    x = 0
    for fold in main_folder.sub_folders:
        if fold.path == event:
            return 1
    for file in main_folder.files:
        if file == event:
            return 1
    for fold in main_folder.sub_folders:
        x += check_if_exist_path(fold, event)
    return x


def rebuild_folder_map():
    global main_folder
    main_folder1 = utils.Folder(folder_path)
    my_directory1 = os.listdir(folder_path)
    utils.build_folders_map(main_folder1, my_directory1, backslash, folder_path)
    main_folder = main_folder1


def on_created(event):
    print(f"hey, {event.src_path} has been created!")
    if os.path.exists(event.src_path):
        server_socket, temp_user_id, temp_comp_id = start_connection(user_id, comp_id, folder_path)
        ack = server_socket.recv(1024)
        server_socket.send(b'true')
        ack1 = server_socket.recv(1024)
        relative = utils.get_relative_path(event.src_path, main_folder.path)
        server_socket.send((relative + str(1000 - len(relative)) + '0' + str(CREATE)).encode())
        ack2 = server_socket.recv(1024)
        if ack2 != b'bye':
            tmp_path, extension = os.path.splitext(event.src_path)
            if os.path.isfile(event.src_path) or '' != extension:
                utils.send_file(event.src_path, main_folder.path, server_socket, user_id)
            else:
                folder_to_add = utils.Folder(event.src_path)
                folder_to_add_directory = os.listdir(event.src_path)
                utils.build_folders_map(folder_to_add, folder_to_add_directory, backslash, event.src_path)
                utils.upload_to_cloud(folder_to_add, event.src_path, server_socket, user_id)
            server_socket.send(b'enough')
            ack3 = server_socket.recv(1024)
        server_socket.close()
        rebuild_folder_map()


def on_deleted(event):
    print(f"what the f**k! Someone deleted {event.src_path}!")
    server_socket, temp_user_id, temp_comp_id = start_connection(user_id, comp_id, folder_path)
    ack = server_socket.recv(1024)
    server_socket.send(b'true')
    ack1 = server_socket.recv(1024)
    relative = utils.get_relative_path(event.src_path, main_folder.path)
    server_socket.send((relative + str(1000 - len(relative)) + '0' + str(DELETE)).encode())
    ack2 = server_socket.recv(1024)
    server_socket.close()
    rebuild_folder_map()


def update_delete(src_path):
    server_socket, temp_user_id, temp_comp_id = start_connection(user_id, comp_id, folder_path)
    ack = server_socket.recv(1024)
    server_socket.send(b'true')
    ack1 = server_socket.recv(1024)
    relative = utils.get_relative_path(src_path, main_folder.path)
    server_socket.send((relative + str(1000 - len(relative)) + '0' + str(DELETE)).encode())
    ack2 = server_socket.recv(1024)
    server_socket.close()
    rebuild_folder_map()


def update_create(dst_path):
    server_socket, temp_user_id, temp_comp_id = start_connection(user_id, comp_id, folder_path)
    ack = server_socket.recv(1024)
    server_socket.send(b'true')
    ack1 = server_socket.recv(1024)
    relative = utils.get_relative_path(dst_path, main_folder.path)
    # Send the server dst header
    server_socket.send((relative + str(1000 - len(relative)) + '0' + str(CREATE)).encode())
    # get ack for the header
    ack2 = server_socket.recv(1024)
    if os.path.isfile(dst_path):
        utils.send_file(dst_path, main_folder.path, server_socket, user_id)
    server_socket.send(b'enough')
    ack3 = server_socket.recv(1024)
    server_socket.close()
    rebuild_folder_map()


def on_moved(event):
    print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")
    # FOR CONTINUE WITH UPDATE FILES WE NEED TO SCAN ALL THE 'MAIN_FOLDER' MAP
    # AND THE IF THE SRC.PATH DIDN'T EXIST ITS A SIGN THAT UPDATE ARE OCCURRED
    if 0 != check_if_exist_path(main_folder, event.src_path):
        server_socket, temp_user_id, temp_comp_id = start_connection(user_id, comp_id, folder_path)
        ack = server_socket.recv(1024)
        server_socket.send(b'true')
        ack1 = server_socket.recv(1024)
        relative = utils.get_relative_path(event.dest_path, main_folder.path)
        # Send the server dst header
        server_socket.send((relative + str(1000 - len(relative)) + '0' + str(CREATE)).encode())
        # get ack for the header
        ack2 = server_socket.recv(1024)
        if ack2 != b'bye':
            tmp_path, extension = os.path.splitext(event.dest_path)
            if os.path.isfile(event.dest_path) or '' != extension:
                utils.send_file(event.dest_path, main_folder.path, server_socket, user_id)
            else:
                folder_to_add = utils.Folder(event.dest_path)
                folder_to_add_directory = os.listdir(event.dest_path)
                utils.build_folders_map(folder_to_add, folder_to_add_directory, backslash, event.dest_path)
                utils.upload_to_cloud(folder_to_add, event.dest_path, server_socket, user_id)
            server_socket.send(b'enough')
            ack3 = server_socket.recv(1024)
            server_socket.close()
            rebuild_folder_map()
            # Delete the source of what we create
            server_socket, temp_user_id, temp_comp_id = start_connection(user_id, comp_id, folder_path)
            ack = server_socket.recv(1024)
            server_socket.send(b'true')
            ack1 = server_socket.recv(1024)
            relative = utils.get_relative_path(event.src_path, main_folder.path)
            server_socket.send((relative + str(1000 - len(relative)) + '0' + str(DELETE)).encode())
            ack2 = server_socket.recv(1024)
        server_socket.close()
        rebuild_folder_map()
    else:
        update_delete(event.dest_path)
        update_create(event.dest_path)


def start_connection(user_id, comp_id, folder_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((ip_server, int(port_server)))
    # Make sure the server know who am i
    server_socket.send(user_id)
    temp_user_id = server_socket.recv(1024)
    server_socket.send(comp_id)
    temp_comp_id = server_socket.recv(1024)
    server_socket.send(str.encode(folder_path))
    return server_socket, temp_user_id, temp_comp_id


# Initialize all the variable we got as arguments
ip_server = sys.argv[1]
port_server = sys.argv[2]
folder_path = sys.argv[3]
time_temp = sys.argv[4]
# Set default id for case the is isn't define by an argument
user_id = '0'
comp_id = b'0'
if len(sys.argv) == 6:
    user_id = sys.argv[5]
# Check which platform the user using to define how to apart folders in the files path
backslash = utils.get_backslash()
my_directory = os.listdir(folder_path)
main_folder = utils.Folder(folder_path)
patterns = ["*"]
ignore_patterns = None
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_moved = on_moved
path = "."
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, main_folder.path, go_recursively)
my_observer.start()

server_socket, temp_user_id, comp_id = start_connection(user_id.encode(), comp_id, folder_path)
# If the ID doesnt exist get new id and build folders map
if temp_user_id != user_id.encode():
    utils.build_folders_map(main_folder, my_directory, backslash, folder_path)
    user_id = temp_user_id
    # Start sync folders map
    utils.copy_data(main_folder, main_folder.path, server_socket, user_id)
    # utils.upload_to_cloud(main_folder, main_folder.path, s, user_id)
    server_socket.send(b'enough')
else:
    utils.get_files(main_folder.path, server_socket)
server_socket.close()

try:
    while True:
        time.sleep(int(time_temp))
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()