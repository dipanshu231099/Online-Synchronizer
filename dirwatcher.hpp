#include <dirent.h>
#include <vector>
#include <string>
#include <iostream>
#include <sys/types.h>
#include <sys/stat.h>


using namespace std;


vector<string> getAllFiles(string directory) {
    vector<string> files;
    struct dirent *dp;
    struct stat fs;
    DIR *dir = opendir(directory.c_str());
    if (!dir)
        return files;
    while ((dp = readdir(dir)) != NULL)
    {
        cout<<dp->d_name<<endl;
        if(string(dp->d_name) != "." && string(dp->d_name)!="..")getAllFiles(directory+"/"+dp->d_name);
        stat((directory+dp->d_name).c_str(), &fs);
    }
    return files;
}