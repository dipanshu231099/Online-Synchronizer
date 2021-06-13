#!/usr/bin/python3

# *** Database Structure ***
# home dir contains "sync_directories"
# "sync_directories" :-
# 						rootdb.db - meta info for all synced dirs
#						[dir_path {/->$$$$}].db - info for synced dir on that path 

# *** Schema ***
# Database     Table
# rootdb.db -> rootdb (store all dirs synced) :- path,unique_key,sync_mode;	[rootdb (fpath text,Hashkey text, mode text)]
#  
# [dir_path {/->$$$$}].db -> info (store all files in synced dir) :- path,modify_time [info (fname text, mtime text)]


# *** libraries ****
import sqlite3 as sqlite
import string
import random
import hashlib
import os
import sys
from datetime import datetime
import time
from pathlib import Path
from getmac import get_mac_address as gma
import threading



# *** Global vars ***
Home_address = str(Path.home())
pathDB = Home_address+"/sync_directories/"
ROOT_DB = "rootdb.db"



# *** Functions ***

# get all files in dir i.e absolute paths
def findFileStats(path):
    current_dir = os.getcwd()
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            abs_path = os.path.join(current_dir, r, file)
            files.append((abs_path, os.path.getmtime(abs_path)))
    return files


# unique key for synced dir
def genHash():
    hash = datetime.now().strftime("%Y%m%d%H%M%S%f")
    hash=gma()+"-"+hash
    return hash


# database connection
def connection(db_file):
    conn = None
    try: 
        conn = sqlite.connect(db_file)
    except sqlite.Error as err:
        print(err)
    return conn


# initialize to sync a dir
def initialize_dir(path):
    key = genHash()
    path = os.path.abspath(path)
    db_name = path.replace('/','$$$$')


    db_name += '.db'
    dir_info = findFileStats(path)
    if len(dir_info)<1:
        raise Exception("Error: Trying to sync empty directory | If intended --> delete directory and sync")

    # if sync lower dir tell higher is synced ??
    root_conn = sqlite.connect(pathDB+ROOT_DB)
    root_cur = root_conn.cursor()
    command = "insert into rootdb values ('{}','{}','automatic')".format(str(path), str(key))
    root_cur.execute(command)
    root_conn.commit()
    root_conn.close()

    init_conn = sqlite.connect(pathDB+db_name)
    init_cur = init_conn.cursor()
    command = "create table if not exists info (fname text, mtime text)"
    init_cur.execute(command)
    for i in range(len(dir_info)):
        command = "insert into info values ('{}','{}')".format(str(dir_info[i][0]), str(dir_info[i][1]))
        init_cur.execute(command)
    init_conn.commit()
    init_conn.close()    


# find modifications in synced dir
# returns :
#            0,                                             if no files to be synced    (type: int)
#            {new:[...], deleted:[...], modified:[...]}, otherwise                    (type: dictionary) 
def check_dir_modifications(path):
    db_name = os.path.abspath(path).replace('/','$$$$'); db_name += '.db'
    dir_info = findFileStats(path)

    conn = sqlite.connect(pathDB+db_name)
    conn_cursor = conn.cursor()

    result = {"new":[], "deleted":[], "modified":[]}

    # get new & modified files
    for i in range(len(dir_info)):
        file = dir_info[i][0]; latest_modify_time = dir_info[i][1]
        command = "SELECT mtime FROM info WHERE fname='{}'".format(file)
        conn_cursor.execute(command)
        records=conn_cursor.fetchall()

        if len(records)==0:
            result["new"].append(file)
            command = "INSERT INTO info VALUES ('{}','{}')".format(str(file),str(latest_modify_time))
            conn_cursor.execute(command)
        elif latest_modify_time!=float(records[0][0]):
            result["modified"].append(file)
            command = "UPDATE info SET mtime= '{}' WHERE fname='{}'".format(latest_modify_time,file)
            conn_cursor.execute(command)

    # get deleted files
    latest_file_set = set([i[0] for i in dir_info])
    command = "SELECT fname FROM info"
    conn_cursor.execute(command)
    records = conn_cursor.fetchall()
    records = [record[0] for record in records]

    for record in records:
        if record not in latest_file_set:
            result["deleted"].append(record)
            command = "DELETE FROM info WHERE fname='{}'".format(str(record))
            conn_cursor.execute(command)

    conn.commit()
    conn.close()

    if(len(result["new"])==0 and len(result["deleted"])==0 and len(result["modified"])==0):
        return 0

    return result


# change sync mode for dir
def changeMode(key, new_mode):
    conn = sqlite.connect(pathDB+ROOT_DB)
    conn_cursor = conn.cursor()
    command = "update rootdb set mode='{}' where Hashkey='{}'".format(str(new_mode), key)
    conn_cursor.execute(command)
    conn.commit()
    conn.close()


# create root database which stores info for dir to be synced [path,key,sync_mode]
def RootDbCreator():

    Path(pathDB).mkdir(parents=True, exist_ok=True)

    db_name = ROOT_DB
    init_conn = sqlite.connect(pathDB+db_name)
    init_cur = init_conn.cursor()
    command = "create table if not exists rootdb (fpath text,Hashkey text, mode text)" # to see if seperate upload frequency can be set
    init_cur.execute(command)
    init_conn.commit()
    init_conn.close()


# show all synced dirs to choose from
def showSyncedDirs():
    conn = sqlite.connect(pathDB+ROOT_DB)
    cur = conn.cursor()
    command = "SELECT fpath,Hashkey,mode FROM rootdb"
    cur.execute(command)
    showRecords = cur.fetchall()

    print("(Directory\tKey\tMode)")
    for showRecord in showRecords:
        tup = "{} \t {} \t {}".format(showRecord[0],showRecord[1],showRecord[2])
        print(tup)

    conn.commit()
    conn.close()


# sync with remote server
def syncFunction(data):
    print("sync.......")
    print(data)


# manual sync dir
def manualSync(key):
    conn = sqlite.connect(pathDB+ROOT_DB)
    conn_cursor = conn.cursor()
    command = "SELECT fpath FROM rootdb Where Hashkey='{}'".format(key)
    conn_cursor.execute(command)
    record = conn_cursor.fetchall()
    conn.commit()
    conn.close()

    dir_path = record[0][0]
    modified_data = check_dir_modifications(dir_path)
    if not not modified_data:
        manual_thread = threading.Thread(target=syncFunction, args=(modified_data,))
        manual_thread.start()
        manual_thread.join()


# TODO
# syncFunction (Team2 doing)

# manual sync
# change sync mode (provide all dirs synced - choose by key)?

# log file - synced or not (server response) -> sync on network
# get dir back

# CLI
