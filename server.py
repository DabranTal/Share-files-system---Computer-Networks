import copy
import random
import socket
import string
import sys
import utils
import os
ADD_FOLDER = 5
CREATE = '1'
UPDATE = '3'
DELETE = '4'


def run_operations(user_id, comp_user, client_socket):
    operations = split_operations(data_dic[user_id][comp_user].actions)
    for op in operations:
        if op[1] is DELETE:
            os.remove(os.path.join(user_folder_path, op[0]))
        elif op[1] is CREATE:
            utils.send_file(op[0], user_folder_path, client_socket)


def upload_files_to_folder(file_name, folder_path, got_from_recv):
    with open(folder_path + backslash + file_name, 'wb') as new_file:
        while got_from_recv != b'stop':
            new_file.write(got_from_recv)
            got_from_recv = client_socket.recv(1024)
            client_socket.send(b'ack')
        new_file.close()
        client_socket.send(b'ack')


def this_update_loop(action_to_add, comp):
    may_update = action_to_add + DELETE + action_to_add + CREATE
    history_actions = data_dic[user_id][comp].history
    if history_actions.endswith(may_update):
        return True
    else:
        return False


def update_actions(user_id, comp_user, header):
    header = utils.data_analysis(header)
    for comp in data_dic[user_id]:
        if comp != comp_user:
            action_to_add = '|' + header[3] + ','
            if not (this_update_loop(action_to_add, comp)):
                data_dic[user_id][comp].actions = data_dic[user_id][comp].actions + '|' + header[3] + ',' + header[0]


def update_b0():
    client_socket.send(b'ack')
    updated_folder = utils.Folder(user_folder_path)
    updated_folder_directory = os.listdir(user_folder_path)
    utils.build_folders_map(updated_folder, updated_folder_directory, backslash, user_folder_path)
    data_dic[user_id]['0'].folders_map = updated_folder
    update_actions(user_id, comp_user, actions)
    break_point = 'here'


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
        data_dic[user_id] = {user_dictionary.comp_id: user_dictionary}
        must_update = utils.User_Dic(0)
        must_update.folders_map = user_dictionary.folders_map
        data_dic[user_id]['0'] = must_update
    else:
        if user_dictionary.comp_id in data_dic[user_id]:
            data_dic[user_id][user_dictionary.comp_id] = user_dictionary
            data_dic[user_id]['0'] = user_dictionary
        else:
            data_dic[user_id] = {user_dictionary.comp_id: user_dictionary}

# create user dictionary
data_dic = {}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', int(sys.argv[1])))
server.listen(0)
if len(sys.argv) != 2:
    exit()
while True:
    client_socket, client_address = server.accept()
    ack_flag = 0
    print('Connection from: ', client_address)
    backslash = utils.get_backslash()
    # Client sent the Id
    user_id = client_socket.recv(1024)
    # Case the user is new
    if user_id.decode('utf-8') == '0':
        id_user = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        client_socket.send(str.encode(id_user))
        comp_user = client_socket.recv(1024)
        comp_user = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        client_socket.send(str.encode(comp_user))
        client_path = client_socket.recv(1024)
        client_path = client_path.decode('utf-8')
        user_dictionary = utils.User_Dic(comp_user)
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
        comp_user = client_socket.recv(1024)
        comp_user = comp_user.decode('utf-8')
        if comp_user == '0':
            comp_user = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        client_socket.send(comp_user.encode())
        client_path = client_socket.recv(1024)
        client_socket.send(b'ack')
        client_path = client_path.decode('utf-8')
        user_id = user_id.decode('utf-8')
        user_folder_path = os.path.join(os.getcwd(), user_id)
        # Case user already log in with this computer
        if comp_user in data_dic.get(user_id):
            # run_operations(user_id, comp_user, client_socket)
            there_is_a_changes = client_socket.recv(1024)
            if there_is_a_changes == b'true':
                client_socket.send(b'ack')
                actions = client_socket.recv(1024)
                header = utils.data_analysis(actions)
                # Case the action is create
                if header[0] == CREATE:
                    # Check if the path is folder
                    if os.path.isdir(client_path + backslash + header[3]):
                        # Check if the path already exists
                        if not (os.path.exists(user_folder_path + backslash + header[3])):
                            # send ack to the header
                            client_socket.send(b'ack')
                            if len(os.listdir(client_path + backslash + header[3])) == 0:
                                new_folder = utils.create_a_folder(user_folder_path + backslash + header[3], os.getcwd())
                            else:
                                add_folder_path = utils.create_a_folder(header[3], os.getcwd() + backslash + user_id)
                                utils.get_files(add_folder_path, client_socket)
                            update_b0()
                            ack_flag = 1
                    elif not os.path.exists(user_folder_path + backslash + header[3]):
                        # send ack to the header
                        client_socket.send(b'ack')
                        utils.get_files(user_folder_path, client_socket)
                        update_b0()
                        ack_flag = 1
                # Case we want delete folder or file
                elif header[0] == DELETE and os.path.exists(user_folder_path + backslash + header[3]):
                    # send ack to the header
                    client_socket.send(b'ack')
                    if os.path.isdir(user_folder_path + backslash + header[3]):
                        if len(os.listdir(user_folder_path + backslash + header[3])) == 0:
                            os.rmdir(user_folder_path + backslash + header[3])
                        else:
                            delete_folder_path = user_folder_path + backslash + header[3]
                            folder_to_delete = utils.Folder(delete_folder_path)
                            folder_to_delete_directory = os.listdir(delete_folder_path)
                            utils.build_folders_map(folder_to_delete, folder_to_delete_directory, backslash,
                                                    delete_folder_path)
                            utils.delete_from_cloud(folder_to_delete, delete_folder_path)
                            os.rmdir(user_folder_path + backslash + header[3])
                    else:
                        os.remove(user_folder_path + backslash + header[3])
                    update_b0()
                    ack_flag = 1
                # dont send ack to the header
                if ack_flag == 0:
                    client_socket.send(b'bye')
            else:
                to_do_list = split_operations(data_dic.get(user_id).get(comp_user).actions)
                for action in to_do_list:
                    if action[1] == DELETE:
                        if os.path.isfile(os.path.join(user_folder_path, action[0])):
                            new_action = action[0] + str(1000 - len(action[0])) + 'f' + DELETE
                        else:
                            new_action = action[0] + str(1000 - len(action[0])) + 'd' + DELETE
                        new_action = new_action.encode()
                        client_socket.send(new_action)
                        ack = client_socket.recv(1024)
                    if action[1] == CREATE:
                        # Check if the client need to create file or directory
                        to_create = os.path.join(user_folder_path, action[0])
                        if os.path.isfile(to_create):
                            new_action = action[0] + str(1000 - len(action[0])) + 'f' + CREATE
                            new_action = new_action.encode()
                            client_socket.send(new_action)
                            ack = client_socket.recv(1024)
                            utils.send_file(to_create, user_folder_path, client_socket)
                            client_socket.send(b'enough')
                            ack = client_socket.recv(1024)
                        else:
                            if len(os.listdir(to_create)) == 0:
                                new_action = action[0] + str(1000 - len(action[0])) + 'e' + CREATE
                            else:
                                new_action = action[0] + str(1000 - len(action[0])) + 'd' + CREATE
                            new_action = new_action.encode()
                            client_socket.send(new_action)
                            ack = client_socket.recv(1024)
                            folder_to_add = utils.Folder(to_create)
                            folder_to_add_directory = os.listdir(to_create)
                            utils.build_folders_map(folder_to_add, folder_to_add_directory, backslash, to_create)
                            utils.upload_to_cloud(folder_to_add, to_create, client_socket, user_id)
                            if len(os.listdir(to_create)) != 0:
                                client_socket.send(b'enough')
                client_socket.send(b'enough')
                """"
                This Ack doesn't get somehow!!
                """
                ack = client_socket.recv(1024)
                data_dic[user_id][comp_user].history += data_dic[user_id][comp_user].actions
                data_dic[user_id][comp_user].actions = ''
                print(comp_user)
        # Case user didn't log in yet with this computer
        else:
            # copy the user files to the new computer
            utils.copy_data(data_dic.get(user_id).get('0').folders_map, user_folder_path, client_socket, user_id)
            client_socket.send(b'enough')
            # data_dic[user_id][comp_user] = data_dic.get(user_id).get('0')
            data_dic[user_id][comp_user] = copy.deepcopy(data_dic.get(user_id).get('0'))
            data_dic[user_id][comp_user].history += data_dic[user_id][comp_user].actions
            data_dic[user_id][comp_user].actions = ''
    client_socket.close()
    print('Client disconnected')