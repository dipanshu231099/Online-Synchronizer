import socket
import tqdm
import os
from _thread import *
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


s = socket.socket()

s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def func(client_socket):
    
    received = client_socket.recv(BUFFER_SIZE).decode()
    print(received,flush=True)
    filename, filesize = received.split(SEPARATOR)

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
    

