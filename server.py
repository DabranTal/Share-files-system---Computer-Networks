import random
import socket
import string
import sys
import utils
import os
ADD_FOLDER = 5
CREATE = 1
UPDATE = 3
DELETE = 4


def run_operations(user_id, client_address, client_socket):
    operations = split_operations(data_dic[user_id][client_address].actions)
    for op in operations:
        if op [1] is DELETE:
            os.remove(user_folder_path + op[0])
        elif op[1] is CREATE:
            utils.create_file(op[0], user_folder_path, client_socket, user_id)


def upload_files_to_folder(file_name, folder_path, got_from_recv):
    with open(folder_path + backslash + file_name, 'wb') as new_file:
        while got_from_recv != b'stop':
            new_file.write(got_from_recv)
            got_from_recv = client_socket.recv(1024)
            client_socket.send(b'ack')
        new_file.close()
        client_socket.send(b'ack')


def update_actions(user_id, client_address, header):
    header = utils.data_analysis(header)
    for address in data_dic[user_id]:
        if address != client_address:
            data_dic[user_id][address].actions = data_dic[user_id][address].actions + '|' + header[3] + ',' + header[0]


def split_operations(operations):
    operation_split = operations.split("|")
    operation_list = []
    for i in range(len(operation_split)):
        if "" == operation_split[i]:
            continue
        operation_list.append(operation_split[i].split(","))
    return operation_list


def update_user_in_data_structure(data_dic, user_id, user_dictionary):
    if user_id not in data_dic:
        data_dic[user_id] = {user_dictionary.address: user_dictionary}
        must_update = utils.User_Dic(0)
        must_update.folders_map = user_dictionary.folders_map
        data_dic[user_id][0] = must_update
    else:
        if user_dictionary.address in data_dic[user_id]:
            data_dic[user_id][user_dictionary.address] = user_dictionary
        else:
            data_dic[user_id] = {user_dictionary.address: user_dictionary}


data_dic = {b'': []}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', int(sys.argv[1])))
server.listen(0)
if len(sys.argv) != 2:
    exit()
while True:
    client_socket, client_address = server.accept()
    user_dictionary = utils.User_Dic(client_address)
    print('Connection from: ', client_address)
    backslash = utils.get_backslash()
    # Client sent the Id
    user_id = client_socket.recv(1024)
    # Case the user is new
    if user_id.decode('utf-8') == '0':
        id_user = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        client_socket.send(str.encode(id_user))
        ack = client_socket.recv(1024)
        # Create main user folder
        user_folder_path = utils.create_a_folder(id_user, os.getcwd())
        # Begin to get files to upload the server cloud
        utils.get_files(user_folder_path, client_socket)
        # Add new user to the server data structure
        user_dictionary.folders_map = utils.Folder(user_folder_path)
        folder_directory = os.listdir(user_folder_path)
        utils.build_folders_map(user_dictionary.folders_map, folder_directory, backslash, user_folder_path)
        update_user_in_data_structure(data_dic, id_user, user_dictionary)
    # Case the user is already exist
    else:
        client_socket.send(user_id)
        ack = client_socket.recv(1024)
        user_id = user_id.decode('utf-8')
        user_folder_path = os.path.join(os.getcwd(), user_id)
        if client_address in data_dic.get(user_id):
            run_operations(user_id, client_address, client_socket)
            there_is_a_changes = client_socket.recv(1024)
            if there_is_a_changes == b'true':
                client_socket.send(b'ack')
                actions = client_socket.recv(1024)
                header = utils.data_analysis(actions)
                client_socket.send(b'ack')
                if header[0] == CREATE:
                    header[3], extension = os.path.splitext(header[3])
                    if '' == extension:
                        new_folder = utils.create_a_folder(header[3], os.getcwd())
                    else:
                        utils.get_files(user_folder_path, client_socket)
                elif header[0] == DELETE:
                    os.remove(user_folder_path + header[3])
                client_socket.send(b'ack')
                update_actions(user_id, client_address, actions)
        else:
            # copy the user files to the new computer
            utils.copy_data(data_dic.get(user_id).get(0).folders_map, user_folder_path, client_socket, user_id)
            client_socket.send(b'enough')
            data_dic[user_id] = {client_address: data_dic.get(user_id).get(0)}



    client_socket.close()
    print('Client disconnected')
