import backend
import sys
import os

os.remove("test.log") if os.path.exists("test.log") else None

Server = backend.Server(port=6567, debug=True, logpath="test.log")
Server.Log("Test", 4)
Server.Log("Test", 4)

with open("test.log", "r") as LogFile:
    LogContents = LogFile.read()

print(LogContents)