# main file

# *** libraries ***
from DirectoryManager import *

#=========== MAIN ==========#
argv = sys.argv[1:]
helpStr = "\n\
help\t\tdisplay the help\n\
init [path]\tinitialise a synchronise for the path\n\
sync \t\tset synchronisation method [manual/automatic] for a synced dir (all synced dirs will be listed to choose from)\n\
snow \t\tsynchronise the directory instantaneously (all synced dirs will be listed to choose from)"
    
if(len(argv)==0):
    print("No arguments passed")

elif(argv[0] == 'help'):
    print(helpStr)
elif(argv[0] == 'init'):
    if not os.path.isfile(pathDB+ROOT_DB):
        RootDbCreator()
    initialize_dir(argv[1])
    print("(Default mode is automatic, if want to change see help)\n")
elif(argv[0] == 'snow'):
    print("**Enter key of the directory to be synced now (dir can be in any mode)**\n")
    showSyncedDirs()
    todo_key = input("\nKey: ")
    manualSync(todo_key)
    

elif(argv[0] == 'sync'):
    print("**Enter key of the directory to change sync method**\n")
    showSyncedDirs()
    todo_key = input("\nKey: ")
    method = int(input("\nChoose synchronisation method\n[1 - automatic] [2 - manual]\nPress 1 or 2: "))

    if((method != 1) and (method != 2)):
        print("##### Error : inconsistent mode ####")
    elif(method == 1):
        changeMode(todo_key, "automatic")
    elif(method == 2):
        changeMode(todo_key, "manual")
    else:
        print("#### Unexpected error ####")

else:
    print("Invalid argument passed")
    print(helpStr)