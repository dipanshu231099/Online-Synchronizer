import sqlite3 as sqlite
import string
import random
from FileStats import findFileStats
import hashlib
import os

def hashPath(path):
    # execute hashing here
    hash = path.split('/')[-1]
    return path

def connection(db_file):
    conn = None
    try: 
        conn = sqlite.connect(db_file)
    except sqlite.Error as e:
        print(e)
    return conn

def initialize_dir(path):
    key = hashPath(path)
    db_name = os.path.abspath(path).replace('/','$$$$')
    db_name += '.db'
    dir_info = findFileStats(path)
    if len(dir_info)<1:
        raise Exception
    init_conn = connection('sync_directories/'+db_name)
    init_cur = init_conn.cursor()
    command = "create table info (fname text, mtime text)"
    init_cur.execute(command)
    for i in range(len(dir_info)):
        command = "insert into info values ('{}','{}')".format(str(dir_info[i][0]), str(dir_info[i][1]))
        init_cur.execute(command)
    init_conn.commit()
    init_conn.close()

initialize_dir('testdir')