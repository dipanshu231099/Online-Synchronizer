'''
Overview :
- get all dirs with auto sync
- check if updated
- create thread for sync, if updated
- wait to match freq of auto sync
'''

# *** libraries ***
import threading
from DirectoryManager import *

# =========== MAIN ==============
# create root database
if not os.path.isfile(pathDB+ROOT_DB):
	RootDbCreator()


# automatic sync
# sync dirs (mode=automatic) with a thread for each dir (frequency for sync : 30mins)
while(1):
	conn = sqlite.connect(pathDB+ROOT_DB)
	conn_cursor = conn.cursor()
	command = "SELECT fpath FROM rootdb Where mode='automatic'"
	conn_cursor.execute(command)
	records = conn_cursor.fetchall()
	conn.commit()
	conn.close()

	path_records = [record[0] for record in records]
	len_records = len(path_records)
	threads = []
	for i in range(len_records):
		modified_data = check_dir_modifications(path_records[i])


		conn = sqlite.connect(pathDB+ROOT_DB)
		conn_cursor = conn.cursor()
		command = "SELECT Hashkey FROM rootdb Where fpath='{}'".format(path_records[i])
		conn_cursor.execute(command)
		records = conn_cursor.fetchall()
		key = records[0][0]
		conn.commit()
		conn.close()



		if not not modified_data:
			new_thread = threading.Thread(target=syncFunction, args=(modified_data,key,))
			threads.append(new_thread)
			new_thread.start()

	threads_count = len(threads)
	for i in range(threads_count):
		threads[i].join()

	# wait (seconds)
	time.sleep(15)
