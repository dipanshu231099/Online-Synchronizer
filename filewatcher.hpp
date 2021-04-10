#include <iostream>
#include <ctime>
#include <sys/types.h>
#include <sys/stat.h>
#include <string>

using namespace std;

class fileInfo {
private:
    string filepath;
    long long int size;
    struct stat fileStats;
    int fstatus;

public:
    fileInfo(string fpath) {
        stat(fpath.c_str(), &fileStats);
    }

    string getModificationTime() {
        return string(ctime(&fileStats.st_mtimespec.tv_sec));
    }

    long long getFileSize() {
        return (long long int)(fileStats.st_size);
    }
};