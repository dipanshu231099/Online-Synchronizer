import socket
import tqdm
import os
from concurrent.futures import ThreadPoolExecutor

from queue import Queue
from _thread import *
import threading
def send_file(s , filename):
    filesize = os.path.getsize(filename)
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                
                break
            
            s.sendall(bytes_read)
            
            progress.update(len(bytes_read))

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 

changes = []
input_filename = input("Enter filename:")
changes.append(input_filename)
host = "127.0.0.1"
port = 5001
s = socket.socket()
print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")
for items in changes:
    send_file(s,items)
s.close()