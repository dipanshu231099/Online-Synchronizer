'''
Overview :
get all dirs with auto sync
check if updated
create thread for sync, if updated
wait to match freq of auto sync
'''

import sqlite3 as sqlite
import time
import threading
from DirectoryManager import check_dir_modifications

def syncFunction(data):
	print("sync.......")


while(1):
	conn = sqlite.connect('sync_directories/rootdb.db')
	conn_cursor = conn.cursor()
	command = "SELECT fpath FROM rootdb"
	conn_cursor.execute(command)
	records = conn_cursor.fetchall()
	path_records = [record[0] for record in records]

	len_records = len(path_records)
	threads = []
	for i in range(len_records):
		modified_data = check_dir_modifications(path_records[i])
		if not not modified_data:
			new_thread = threading.Thread(target=syncFunction, args=(modified_data,))	# todo: syncFunction
			threads.append(new_thread)
			new_thread.start()

	threads_count = len(threads)
	for i in range(threads_count):
		threads[i].join()

	# wait (seconds)
	time.sleep(30*60)
