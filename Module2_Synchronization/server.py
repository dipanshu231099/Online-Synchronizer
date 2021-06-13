import socket
import tqdm
import os
from _thread import *
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

TODO_FILE = "./.todo"



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


# -->
def mark_deleted(filename, timestamp, todo_address):
    f = open(TODO_FILE,"a")
    f.write()

    return None

# -->
def log_insert(filename , operation_code , timestamp):
    return None

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

def operation_resolve(client_socket):  #aka contextSetter
    message = client_socket.split(SEPARATOR)
    operation = message[0]
    path = message[1]
    if(operation=="modify"):
        size = message[2] 
        return message,path,size
    else:
        #operation is delete
        return message, path, None
    

def syncHandler(client_socket):

    operation,path,size = operation_resolve(client_socket)
    
    received = client_socket.recv(BUFFER_SIZE).decode()

    #check condition here for delete message and update todo

    
    print(received,flush=True)
    header, filepath, content = received.split(SEPARATOR)
    if(header=="delete"):
        print("file deleted detected")
        
    else:
        filename = header
        filesize = content
    #filename, filesize = received.split(SEPARATOR)

        filename = os.path.basename(filename)

        filesize = int(filesize)


        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open("hello_", "wb") as f:
            while True:
                
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                        break
                
                f.write(bytes_read)
                
                progress.update(len(bytes_read))

    #print("yup",flush =True)
    client_socket.close()

    #s.close()


tmp=0
while (1):
    client_socket, address = s.accept() 

    print(f"[+] {address} is connected.")
    start_new_thread(func, (client_socket,))
s.close()
    

