import os

current_dir = os.getcwd()

def findFileStats(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            abs_path = os.path.join(current_dir, r, file)
            files.append((abs_path, os.path.getmtime(abs_path)))
    return files
