import sqlite3 as sqlite
import string
import random
from FileStats import findFileStats
import hashlib
import os
import sys
from datetime import datetime

ROOT_DB = "rootdb.db"

def genHash():
    # execute hashing here
    hash = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return hash

def connection(db_file):
    conn = None
    try: 
        conn = sqlite.connect(db_file)
    except sqlite.Error as err:
        print(err)
    return conn

def initialize_dir(path):
    key = genHash()
    db_name = os.path.abspath(path).replace('/','$$$$')
    db_name += '.db'
    dir_info = findFileStats(path)
    if len(dir_info)<1:
        raise Exception("Error: Trying to sync empty directory | If intended --> delete directory and sync")

    # if sync lower dir tell higher is synced ??
    root_conn = sqlite.connect('sync_directories/'+ROOT_DB)
    root_cur = root_conn.cursor()
    command = "insert into rootdb values ('{}','{}','automatic')".format(str(path), str(key))
    root_cur.execute(command)
    root_conn.commit()
    root_conn.close()

    init_conn = sqlite.connect('sync_directories/'+db_name)
    init_cur = init_conn.cursor()
    command = "create table if not exists info (fname text, mtime text)"
    init_cur.execute(command)
    for i in range(len(dir_info)):
        command = "insert into info values ('{}','{}')".format(str(dir_info[i][0]), str(dir_info[i][1]))
        init_cur.execute(command)
    init_conn.commit()
    init_conn.close()    


# returns :
#            0,                                             if no files to be synced    (type: int)
#            {new:[...], deleted:[...], modified:[...]}, otherwise                    (type: dictionary) 
def check_dir_modifications(path):
    db_name = os.path.abspath(path).replace('/','$$$$'); db_name += '.db'
    dir_info = findFileStats(path)

    conn = sqlite.connect('sync_directories/'+db_name)
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

def changeMode(path, new_mode):
    db_name = ROOT_DB
    path = os.path.abspath(path)
    mod_conn = sqlite.connect('sync_directories/'+db_name)
    mod_cur = mod_conn.cursor()
    command = "update rootdb set mode='{}' where fpath='{}'".format(str(new_mode), str(path))

def RootDbCreator():
    db_name = ROOT_DB
    init_conn = sqlite.connect('sync_directories/'+db_name)
    init_cur = init_conn.cursor()
    command = "create table if not exists rootdb (fpath text,Hashkey text, mode text)" # to see if seperate upload frequency can be set
    init_cur.execute(command)
    init_conn.commit()
    init_conn.close()


#=========== MAIN ==========#
argv = sys.argv[1:]
helpStr = "\n\
help\t\tdisplay the help\n\
init [path]\tinitialise a synchronise for this path\n\
sync [path, mode]\tset synchronisation method, (automatic and manual)\n\
snow [path]\tsynchronise the directory instaneously"
    
if(len(argv)==0):
    print("No arguments passed")

elif(argv[0] == 'help'):
    print(helpStr)
elif(argv[0] == 'init'):
    initialize_dir(argv[1])

elif(argv[0] == 'snow'):
    # synchronise
    pass

elif(argv[0] == 'sync'):
    if(len(argv)<3):
        print('sync mode works on 3 args.',len(argv),'were provided.')
    elif(argv[2] == 'automatic'):
        changeMode(argv[1], argv[2])
    elif(argv[2] == 'manual'):
        changeMode(argv[1], argv[2])
    else:
        print("inconsistent mode")
        print(helpStr)

else:
    print("Invalid argument passed")
    print(helpStr)