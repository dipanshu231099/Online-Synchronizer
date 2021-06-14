import socket
import tqdm
import os
from concurrent.futures import ThreadPoolExecutor

from queue import Queue
from _thread import *
import threading
from shutil import make_archive
import errno

    
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
    sockid.connect((serverIP, serverPort)) 
    #sockid.send("hello world".encode())
    try:
        print("In try")
        
        #print("getSerSide path",getServerSidePath(modified[0], syncFolderAbsolutePath, syncFolderKey))
        for f in modified:
            send_file(sockid, getServerSidePath(f, syncFolderAbsolutePath, syncFolderKey) , f )
        for f in new:
            send_file(sockid, getServerSidePath(f, syncFolderAbsolutePath, syncFolderKey) , f)
        for f in delete:
            # make message to with header and filename to notify server to just update .tobedeleated file on server side
            msg = make_delete_msg(getServerSidePath(f, syncFolderAbsolutePath, syncFolderKey))
            send_message(sockid, msg)  
        syncStatus = True

    except Exception as e: 
        print("something's wrong with %s:%d. Exception is %s" % (serverIP, serverPort, e))
    finally:
        print("in finally")
        sockid.close()

    return syncStatus

'''
takes a fileAbsolutePath, removes syncFolderAbsolutePath and makes it relative path from a folder named syncFolderKey
returns that new path
'''
def getServerSidePath(fileAbsolutePath, syncFolderAbsolutePath, syncFolderKey):
    return "./"+syncFolderKey+remove_prefix(fileAbsolutePath, syncFolderAbsolutePath)

def send_file(s, filename , filenme_wrt_client):
    filesize = os.path.getsize(filenme_wrt_client)
    HEADER = "SEND"
    print("message made:",f"{HEADER}{SEPARATOR}{filename}{SEPARATOR}{filesize}")
    print(s.send(f"{HEADER}{SEPARATOR}{filename}{SEPARATOR}{filesize}".encode()) , "no of bytes send") 
    
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filenme_wrt_client, "rb") as f:
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

def reqFolderSync(syncFolderKey, serverIP, serverPort):
    downloadStatus = False

    sockid = socket.socket()
    try:
        sockid.connect((serverIP, serverPort)) 

        HEADER = "DOWNLOAD"
        msg = f"{HEADER}{SEPARATOR}{syncFolderKey}{SEPARATOR}".encode()
        sockid.send(msg)

        received = sockid.recv(BUFFER_SIZE).decode()
        HEADER, zipfilename, zipfilesize = received.split(SEPARATOR)
        
        if (HEADER == "NOT_FOUND"):
            print("FOLDER NOT FOUND")
        else:
            receiveFile(zipfilename, zipfilesize, sockid)

        downloadStatus = True

    except Exception as e: 
        print("something's wrong with %s:%d. Exception is %s" % (serverIP, serverPort, e))

    finally:
        print("in finally")
        sockid.close()

    return downloadStatus

def receiveFile(filename, filesize, client_socket):

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    filesize = int(filesize)
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                break

            f.write(bytes_read)
            
            progress.update(len(bytes_read))


def send_message(socketfd, msg):
    socketfd.send(msg)

def downloadReqFile(filepath):
    pass
