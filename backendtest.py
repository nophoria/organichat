import backend
import sys
import os
import threading
import time

def ClearLog():
    if os.path.exists("test.log"): 
        os.remove("test.log")

def RunServerBackground(Server):
    try:
        Server.Run()
    except Exception as e:
        sys.exit(f"Server Run Failed Err {e}")

ClearLog()

try:
    Server = backend.Server(port=6567, debug=True, logpath="test.log")
    BackendHandler = backend.BackendHandler(ServerIP="localhost", Port=6567)
except Exception as e:
    print(f"Server/Backend Handler Init Failed Err {e}")

def ReadLogs():
    LogList = []
    try:
        with open("test.log", "r") as LogFile:
            LogContents = LogFile.readlines()

            LineNum = 0
            for Line in LogContents:
                LineNum += 1
                CleanLine = Line.strip()
                if not CleanLine:
                    raise ValueError("Empty Line Found In Log File")
                    
                LineData = CleanLine.split(", ", 3)
                if len(LineData) == 3:
                    LogList.append(
                        {
                            "line": LineNum,
                            "time": LineData[0],
                            "loglevel": LineData[1],
                            "data": LineData[2]
                        }
                    )
                else:
                    raise ValueError("Invalid Log Format")

    except Exception as e:
        print(f"Error reading logs: {e}")
        return []
    
    return LogList

BatchTestNum = 100

print("Starting Log Tests")

ClearLog()
for i in range(BatchTestNum):
    Server.Log(f"TestingLine{i+1}", ErrLevel=4)
LogList = ReadLogs()

if (len(LogList) != BatchTestNum):
    sys.exit(f"Log Test Failed, Log File Does Not Contain {BatchTestNum} Entries When {BatchTestNum} Entries Logged")

for i in range(BatchTestNum):
    if (LogList[i]["loglevel"] != "[DEBUG]"):
        sys.exit(f"Log Test Failed, Log Level For Line {i+1} Entry Is Not [DEBUG]")

    Expected = f"TestingLine{i+1}"
    Actual = str(LogList[i]["data"])
    
    if (Actual != Expected):
        sys.exit(f"Log Test Failed, Log Data For Line {i+1} Does Not Match Expected Data")

ClearLog()
print("Log Tests Passed")
print("Starting Msg Tests")

server_thread = threading.Thread(target=RunServerBackground, args=(Server,), daemon=True)
server_thread.start()

time.sleep(0.1)

TestMessageList = [f"Test Message {i+1}" for i in range(BatchTestNum)]
for i in range(BatchTestNum):
    BackendHandler.SendMsg(TestMessageList[i])

time.sleep(0.1)

try:
	Pulled = BackendHandler.PullMsgs()
	if Pulled:
		print(f"Received messages: {Pulled}")
	else:
		sys.exit("Test Failed No Data Returned By Server")

except Exception as e:
    sys.exit(f"Error pulling messages: {e}")

print("All Backend Tests Passed")