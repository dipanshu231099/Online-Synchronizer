from datetime import datetime
import socket
import tqdm
import os
from _thread import *
from threading import Thread
import time
import schedule

'''
main server side -> threadArray, serverSocket, reqListen -> MODIFY, DELETE, reqHandler -> new thread -> handover -> ~T/F -> todo -> check -> regular time-intervel~ -> log file write-append
'''

'''
main -> serverSocket open, listen -> accept (non-persistent conncetions) -> syncHandler -> contextSetter -> Modify, Delete (functions) -> 
Delete :: path -> mark_delete -> .tobedeleted write -> path, timestamp
Modify :: path -> direclty modify/create
ActualDelete :: path -> delete
DeleteRoutine (inside main, main will call it in a thread) - sleep -> wake -> every 1 day intervel 
=======================
main, syncHandler, contexSetter, Modify, Delete, ActualDelete, DeleteRoutine
=======================
.tobedeleted -> path, timestamp
'''

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

TOBEDELETED = "./.tobedeleted"  # set to file path of to_delete file

def deleteRoutine():
    
    with open(TOBEDELETED, 'r+') as tobedeleted:
        tasks = tobedeleted.readlines()
        tobedeleted.seek(0)
        for task in tasks:
            filepath, timestamp = task.strip("\n").split(" ")
            delete_date = datetime.fromtimestamp(float(timestamp)/1000)
            curr_date = datetime.now()
            del_days = (curr_date - delete_date).days
            if (del_days >= 30):
                actualDelete(filepath)
            else:
                tobedeleted.write(task)
        tobedeleted.truncate()
    

def actualDelete(filepath):
    try:
        os.remove(filepath)
    except OSError:
        pass 

def mark_deleted(filename, timestamp):
    f = open(TOBEDELETED,"a")
    data_added = filename + " " + str(timestamp) + "\n"
    f.write(data_added)
    return None


def log_insert(filename , operation_code , timestamp):
    return None


def operation_resolve(client_socket):  #aka contextSetter
    received = client_socket.recv(BUFFER_SIZE).decode()
    print(received,flush=True)
    message = received.split(SEPARATOR)
    operation = message[0]
    path = message[1]
    if(operation=="modify"):
        size = message[2] 
        return message,path,size
    else:
        #operation is delete
        return message, path, None
    
def modify(filename, filesize, client_socket):
    filesize = int(filesize)
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                break

            f.write(bytes_read)
            
            progress.update(len(bytes_read))

def delete(filename):
    mark_deleted(filename , time.time())

def syncHandler(client_socket):

    operation, path, size = operation_resolve(client_socket)
    
    if(operation == "DELETE"):
        delete(path)
    else:
        modify(path, size, client_socket)

    client_socket.close()

def main():
    s = socket.socket()

    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
    while (1):
        client_socket, address = s.accept()
        print(f"[+] {address} is connected.")
        start_new_thread(syncHandler, (client_socket,))

    s.close()

if __name__ == "__main__":
    main()