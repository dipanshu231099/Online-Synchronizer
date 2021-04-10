#include <iostream>
#include "filewatcher.hpp"
#include "dirwatcher.hpp"

using namespace std;

int main() {
    fileInfo F = fileInfo("dirwatcher.cpp");
    cout<<F.getModificationTime()<<F.getFileSize()<<endl;
}