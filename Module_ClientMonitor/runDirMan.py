# main file

# *** libraries ***
from DirectoryManager import *

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
    if not os.path.isfile(pathDB+ROOT_DB):
        RootDbCreator()
    initialize_dir(argv[1])
elif(argv[0] == 'snow'):
    print("**Enter key of the directory to be synced now (dir can be in any mode)**\n")
    showSyncedDirs()
    todo_key = input("\nKey: ")
    

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