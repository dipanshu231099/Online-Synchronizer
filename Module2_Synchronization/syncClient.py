import socket
import tqdm
import os
from concurrent.futures import ThreadPoolExecutor

from queue import Queue
from _thread import *
import threading

    
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

'''
Main sync function called by ClientMonitor Module
Arguments - 
    changesDict = {"new": [<absolute filepaths>], "modified": [<absolute filepaths>], "deleted": [<absolute filepaths>]}
    syncFolderKey
    syncFolderAbsolutePath
    serverIP
    serverPort
    =================
    changesDict - C:/a/f/g/h
    syncFolderAbsolutePath - C:/a/f
    syncFolderKey - fh
    servrside - ./fh/g/h
    ./f/g/h
    key
    ./key/g/h
    ===================
'''
def sync(changesDict, syncFolderKey, serverIP, serverPort):

    modified = changesDict["modified"]
    new = changesDict["new"]
    delete = changesDict["deleted"]
    syncFolderAbsolutePath = changesDict["syncFolderPath"]
    syncStatus = False

    sockid = socket.socket()
    try:
        sockid.connect((serverIP, serverPort)) 

        for f in modified:
            send_file(sockid, getServerSidePath(f, syncFolderAbsolutePath, syncFolderKey))
        for f in new:
            send_file(sockid, getServerSidePath(f, syncFolderAbsolutePath, syncFolderKey))
        for f in delete:
            # make message to with header and filename to notify server to just update .tobedeleated file on server side
            msg = make_delete_msg(getServerSidePath(f, syncFolderAbsolutePath, syncFolderKey))
            send_message(sockid, msg)  
        syncStatus = True

    except Exception as e: 
        print("something's wrong with %s:%d. Exception is %s" % (serverIP, serverPort, e))
    finally:
        sockid.close()

    return syncStatus

'''
takes a fileAbsolutePath, removes syncFolderAbsolutePath and makes it relative path from a folder named syncFolderKey
returns that new path
'''
def getServerSidePath(fileAbsolutePath, syncFolderAbsolutePath, syncFolderKey):
    return "./"+syncFolderKey+remove_prefix(fileAbsolutePath, syncFolderAbsolutePath)

def send_file(s, filename):
    filesize = os.path.getsize(filename)
    HEADER = "SEND"
    s.send(f"{HEADER}{SEPARATOR}{filename}{SEPARATOR}{filesize}".encode()) 
    
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read) 
            progress.update(len(bytes_read))

def make_delete_msg(filename):
    #msg contain header which will be checked on server to identify it as deleted file
    HEADER = "DELETE"
    msg = f"{HEADER}{SEPARATOR}{filename}{SEPARATOR}".encode()
    return msg

def send_message(socketfd, msg):
    socketfd.send(msg)
