import backend
import sys
import os

os.remove("test.log") if os.path.exists("test.log") else None

Server = backend.Server(port=6567, debug=True, logpath="test.log")
Server.Log("Test", 4)
Server.Log("Test", 4)

LogList = []
with open("test.log", "r") as LogFile:
    LogContents = LogFile.readlines()

    linenum = 0
    for line in LogContents:
        linenum += 1
        linedata = line.split(", ")
        LogList.append(
            {
                "line": linenum,
                "time": linedata[0],
                "loglevel": linedata[1],
                "data": linedata[2:]
            }
        )


print(LogList)